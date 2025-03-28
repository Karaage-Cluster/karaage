{
  description = "Cluster account management";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    devenv.url = "github:cachix/devenv";
    flockenzeit.url = "github:balsoft/flockenzeit";
  };

  outputs =
    inputs@{
      self,
      nixpkgs,
      flake-utils,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      devenv,
      flockenzeit,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        inherit (nixpkgs) lib;
        pkgs = nixpkgs.legacyPackages.${system};

        build_env = {
          BUILD_DATE = with flockenzeit.lib.splitSecondsSinceEpoch { } self.lastModified; "${F}T${T}${Z}";
          VCS_REF = "${self.shortRev or self.dirtyShortRev or "dirty"}";
        };

        python = pkgs.python312;

        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        # Create package overlay from workspace.
        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "sdist";
        };

        # Extend generated overlay with build fixups
        #
        # Uv2nix can only work with what it has, and uv.lock is missing essential metadata to perform some builds.
        # This is an additional overlay implementing build fixups.
        # See:
        # - https://pyproject-nix.github.io/uv2nix/FAQ.html
        pyprojectOverrides =
          final: prev:
          # Implement build fixups here.
          # Note that uv2nix is _not_ using Nixpkgs buildPythonPackage.
          # It's using https://pyproject-nix.github.io/pyproject.nix/build.html
          let
            inherit (final) resolveBuildSystem;
            inherit (builtins) mapAttrs;

            # Build system dependencies specified in the shape expected by resolveBuildSystem
            # The empty lists below are lists of optional dependencies.
            #
            # A package `foo` with specification written as:
            # `setuptools-scm[toml]` in pyproject.toml would be written as
            # `foo.setuptools-scm = [ "toml" ]` in Nix
            buildSystemOverrides = {
              asgiref.setuptools = [ ];
              bcrypt.setuptools = [ ];
              certifi.setuptools = [ ];
              cssmin.setuptools = [ ];
              django-ajax-selects.poetry-core = [ ];
              django-environ.setuptools = [ ];
              django-filter.flit-core = [ ];
              django-ranged-response.setuptools = [ ];
              django.setuptools = [ ];
              django-simple-captcha.setuptools = [ ];
              django-tables2.hatchling = [ ];
              gunicorn.setuptools = [ ];
              jsmin.setuptools = [ ];
              ldap3.setuptools = [ ];
              packaging.flit-core = [ ];
              passlib.setuptools = [ ];
              pathspec.flit-core = [ ];
              pip.setuptools = [ ];
              pluggy.setuptools = [ ];
              pyasn1.setuptools = [ ];
              pyjwt.setuptools = [ ];
              python-alogger.setuptools = [ ];
              python-tldap.poetry-core = [ ];
              sentry-sdk.setuptools = [ ];
              six.setuptools = [ ];
              sqlparse.hatchling = [ ];
              urllib3.hatchling = [ ];
              urllib3.hatch-vcs = [ ];
              whitenoise.setuptools = [ ];
            };

          in
          mapAttrs (
            name: spec:
            prev.${name}.overrideAttrs (old: {
              nativeBuildInputs = old.nativeBuildInputs ++ resolveBuildSystem spec;
            })
          ) buildSystemOverrides
          // {
            cracklib = prev.cracklib.overrideAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.cracklib ];
              nativeBuildInputs = old.nativeBuildInputs ++ [
                (resolveBuildSystem {
                  setuptools = [ ];
                })
              ];
            });
            mysqlclient = prev.mysqlclient.overrideAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.libmysqlclient ];
              nativeBuildInputs = old.nativeBuildInputs ++ [
                pkgs.pkg-config
                (resolveBuildSystem { setuptools = [ ]; })
              ];
            });
            psycopg2-binary = prev.psycopg2-binary.overrideAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ pkgs.postgresql ];
              nativeBuildInputs = old.nativeBuildInputs ++ [
                pkgs.pkg-config
                (resolveBuildSystem { setuptools = [ ]; })
              ];
            });
            pillow = prev.pillow.overrideAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [
                pkgs.zlib
                pkgs.libjpeg
              ];
              nativeBuildInputs = old.nativeBuildInputs or [ ] ++ [
                pkgs.pkg-config
                (resolveBuildSystem { setuptools = [ ]; })
              ];
            });
          };

        pythonSet =
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
                pyprojectOverrides
              ]
            );

        inherit (pkgs.callPackages pyproject-nix.build.util { }) mkApplication;
        package = mkApplication {
          venv = pythonSet.mkVirtualEnv "karaage" workspace.deps.default;
          package = pythonSet.karaage;
        };

        slapd = pkgs.writeShellScriptBin "slapd" ''
          exec ${pkgs.openldap}/libexec/slapd "$@"
        '';
        devShell = devenv.lib.mkShell {
          inherit inputs pkgs;
          modules = [
            {
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
                pkgs.gcc
                pkgs.python3
                pkgs.uv
                pkgs.docker-compose
                pkgs.dockerfile-language-server-nodejs
              ];
              enterShell = ''
                export KARAAGE_CONFIG_FILE=./dev_settings.py
                export LD_LIBRARY_PATH="${pkgs.cracklib}/lib:$LD_LIBRARY_PATH"
                export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock
                export BUILD_DATE="${build_env.BUILD_DATE}"
                export VCS_REF="${build_env.VCS_REF}"
              '';
              services.mysql = {
                enable = true;
                package = pkgs.mariadb;
                ensureUsers = [
                  {
                    name = "karaage";
                    password = "q1w2e3r4";
                    ensurePermissions = {
                      "karaage.*" = "ALL PRIVILEGES";
                    };
                  }
                ];
                initialDatabases = [ { name = "karaage"; } ];
              };
            }
          ];
        };
      in
      {
        packages = {
          devenv-up = devShell.config.procfileScript;
          karaage = package;
          default = package;
        };

        devShells.default = devShell;
      }
    );
}
