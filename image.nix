let
  sources = import ./nix/sources.nix;
  pkgs = import sources.nixpkgs { };
  me-download-me-reupload = import ./default.nix;
in
pkgs.dockerTools.buildLayeredImage {
  name = "docker.pkg.github.com/ldesgoui/me-download-me-reupload/me-download-me-reupload";
  created = "now";

  contents = [ me-download-me-reupload ];

  config.Cmd = [ "me-download-me-reupload" ];
  config.Env = [ "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt" ];
}
