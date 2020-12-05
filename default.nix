let
  sources = import ./nix/sources.nix;
  pkgs = import sources.nixpkgs { };
in
pkgs.stdenv.mkDerivation {
  pname = "me-download-me-reupload";
  version = "0.1.0";

  src = ./run.py;

  propagatedBuildInputs = [
    (pkgs.python3.withPackages (p: [
      p.youtube-dl
      (p.discordpy.overridePythonAttrs (_: { src = sources."discord.py"; }))
    ]))
  ];

  dontUnpack = true;

  installPhase = ''
    install -D $src $out/bin/me-download-me-reupload
  '';

  doCheck = false;
}
