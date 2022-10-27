{ lib
, buildPythonPackage
, fetchPypi
, torch
, nltk
, scipy
, sentencepiece
, transformers
, scikit-learn
, torchvision
}:

buildPythonPackage rec {
  version = "2.2.2";
  pname = "sentence-transformers";

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-28YBY7J94hB2yaMNJLW3tvoFFB1ozyVT+pp3v3mikTY=";
  };

  propagatedBuildInputs = [ torch nltk scipy sentencepiece transformers scikit-learn torchvision ];

  # TODO: fix tests
  doCheck = false;

  meta = with lib; {
    homepage = "https://github.com/UKPLab/sentence-transformers";
    description = "Sentence Transformers: Multilingual Sentence, Paragraph, and Image Embeddings using BERT & Co.";
  };
}
