{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    buildInputs = with pkgs; [
      python38
      python38Packages.fastapi
      python38Packages.pip-tools
      python38Packages.uvicorn
    ];
}
