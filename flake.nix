{
  description = "Cluster account management";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        p2n = import poetry2nix { inherit pkgs; };
        mkPoetryApplication = p2n.mkPoetryApplication;
        pkgs = nixpkgs.legacyPackages.${system};
        slapd = pkgs.writeShellScriptBin "slapd" ''
          exec ${pkgs.openldap}/libexec/slapd "$@"
        '';

      in {
        packages = {
          karaage = p2n.mkPoetryApplication {
            projectDir = self;
            overrides = p2n.overrides.withDefaults (final: prev: {
              #nh3 = prev.nh3.override { preferWheel = true; };
              furo = prev.furo.override { preferWheel = true; };
              cracklib = prev.cracklib.overridePythonAttrs (oldattrs: {
                buildInputs = oldattrs.buildInputs
                  ++ [ final.setuptools pkgs.cracklib ];
              });
              django-filter = prev.django-filter.overridePythonAttrs
                (oldattrs: {
                  buildInputs = oldattrs.buildInputs ++ [ final.flit-core ];
                });
              django-ajax-selects = prev.django-ajax-selects.overridePythonAttrs
                (oldattrs: {
                  buildInputs = oldattrs.buildInputs ++ [ final.setuptools ];
                });
              python-alogger = prev.python-alogger.overridePythonAttrs
                (oldattrs: {
                  buildInputs = oldattrs.buildInputs ++ [ final.setuptools ];
                });
              python-tldap = prev.python-tldap.overridePythonAttrs (oldattrs: {
                buildInputs = oldattrs.buildInputs ++ [ final.poetry-core ];
              });
              bump2version = prev.bump2version.overridePythonAttrs (oldAttrs: {
                buildInputs = oldAttrs.buildInputs ++ [ final.setuptools ];
              });
            });
          };
          default = self.packages.${system}.karaage;
        };

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.poetry
            pkgs.libffi
            slapd
            pkgs.openldap
            pkgs.libmysqlclient
            pkgs.cracklib
            pkgs.pkg-config
            pkgs.sentry-cli
            pkgs.nodejs
          ];
        };
      });
}
