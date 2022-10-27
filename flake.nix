{
  description = "A flake to make these dependencies work";

  inputs = {
    nixlib.url = "github:nix-community/nixpkgs.lib";
    nixpkgs.url = "github:NixOS/nixpkgs";
  };
  outputs = { self, nixpkgs, nixlib }@inputs:
    let
      nixlib = inputs.nixlib.outputs.lib;
      supportedSystems = [ "x86_64-linux" ];
      forAll = nixlib.genAttrs supportedSystems;
      requirements = pkgs: with pkgs; with pkgs.python3.pkgs; [
        python3

        torch
        sentence-transformers
      ];
      overlay_pynixify = self:
        rec {
          sentence-transformers = self.callPackage ./packages/sentence-transformers {};
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
                      (overlay_pynixify python-self);
                  };
                })
              ];
            };
          in
          rec {
            dependencies = nixpkgs_.mkShell {
              name = "dependencies";
              propagatedBuildInputs = requirements nixpkgs_;
              shellHook = ''
              '';
            };
            default = dependencies;
          });
    };
}
