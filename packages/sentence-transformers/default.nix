{ lib
, buildPythonPackage
, fetchPypi
, torch
}:

buildPythonPackage rec {
  version = "2.2.2";
  pname = "sentence-transformers";

  src = fetchPypi {
    inherit pname version;
    sha256 = "4f2a4d39e4ea601b9ab42b2db08b5918a9538c168cff1c6895ae26646f3d73b1";
  };

  propagatedBuildInputs = [ torch ];

  # TODO: fix tests
  doCheck = false;

  meta = with lib; {
    homepage = "https://github.com/UKPLab/sentence-transformers";
    description = "Sentence Transformers: Multilingual Sentence, Paragraph, and Image Embeddings using BERT & Co.";
  };
}
