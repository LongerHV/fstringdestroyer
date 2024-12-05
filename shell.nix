{ pkgs, ... }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3Packages.python
    python3Packages.tree-sitter
    python3Packages.tree-sitter-python
  ];
}
