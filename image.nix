let
  sources = import ./nix/sources.nix;
  pkgs = import sources.nixpkgs { };
  me-download-me-reupload = import ./default.nix;
in
pkgs.dockerTools.buildLayeredImage {
  name = "me-download-me-reupload";

  contents = [ me-download-me-reupload ];

  config.Cmd = [ "me-download-me-reupload" ];
}
