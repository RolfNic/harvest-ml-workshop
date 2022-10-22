{
  description = "A very basic flake";

  inputs = {
    nixlib.url = "github:nix-community/nixpkgs.lib";
    nixpkgs.url = "github:NixOS/nixpkgs?rev=fd54651f5ffb4a36e8463e0c327a78442b26cbe7";
  };
  outputs = { self, nixpkgs, nixlib }@inputs:
    let
      nixlib = inputs.nixlib.outputs.lib;
      supportedSystems = [ "x86_64-linux" ];
      forAll = nixlib.genAttrs supportedSystems;
      requirements = pkgs: with pkgs; with pkgs.python3.pkgs; [
        python3

        torch
        torchvision

        transformers
        sentence-transformers
      ];
      overlay_pynixify = self:
        let
          rm = d: d.overrideAttrs (old: {
            nativeBuildInputs = old.nativeBuildInputs ++ [ self.pythonRelaxDepsHook ];
            pythonRemoveDeps = [ "opencv-python-headless" "opencv-python" "tb-nightly" ];
          });
          callPackage = self.callPackage;
          rmCallPackage = path: args: rm (callPackage path args);
        in
        rec {
          sentence-transformers = callPackage ./packages/sentence-transformers {};
        };
      overlay_amd = nixpkgs: pythonPackages:
        rec {
          torch-bin = pythonPackages.torch-bin.overrideAttrs (old: {
            src = nixpkgs.fetchurl {
              name = "torch-1.12.1+rocm5.1.1-cp310-cp310-linux_x86_64.whl";
              url = "https://download.pytorch.org/whl/rocm5.1.1/torch-1.12.1%2Brocm5.1.1-cp310-cp310-linux_x86_64.whl";
              hash = "sha256-kNShDx88BZjRQhWgnsaJAT8hXnStVMU1ugPNMEJcgnA=";
            };
          });
          torchvision-bin = pythonPackages.torchvision-bin.overrideAttrs (old: {
            src = nixpkgs.fetchurl {
              name = "torchvision-0.13.1+rocm5.1.1-cp310-cp310-linux_x86_64.whl";
              url = "https://download.pytorch.org/whl/rocm5.1.1/torchvision-0.13.1%2Brocm5.1.1-cp310-cp310-linux_x86_64.whl";
              hash = "sha256-mYk4+XNXU6rjpgWfKUDq+5fH/HNPQ5wkEtAgJUDN/Jg=";
            };
          });
          torch = torch-bin;
          torchvision = torchvision-bin;
        };
    in
    {

      devShells = forAll
        (system:
          let
            nixpkgs_ = import inputs.nixpkgs {
              inherit system;
              config.allowUnfree = true; #both CUDA and MKL are unfree
              overlays = [
                (final: prev: {
                  python3 = prev.python3.override {
                    packageOverrides = python-self: python-super:
                      (overlay_amd prev python-super) //
                      (overlay_pynixify python-self);
                  };
                })
              ];
            };
          in
          rec {
            torch-amd = nixpkgs_.mkShell
            (let
              lapack = nixpkgs_.lapack.override { lapackProvider = nixpkgs_.mkl; };
              blas = nixpkgs_.lapack.override { lapackProvider = nixpkgs_.mkl; };
            in
            {
              name = "torch-amd";
              propagatedBuildInputs = requirements nixpkgs_;
              shellHook = ''
                #on my machine SD segfaults somewhere inside scipy with openblas, so I had to use another blas impl
                #build of scipy with non-default blas is broken, therefore overriding lib in runtime

                export NIXPKGS_ALLOW_UNFREE=1
                export LD_LIBRARY_PATH=${lapack}/lib:${blas}/lib
                export HSA_OVERRIDE_GFX_VERSION=10.3.0
              '';
            });
            default = torch-amd;
          });
    };
}
