{
  description = "Pipes terminal screensaver — unofficial Python rewrite of pipes.sh";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          package = pkgs.callPackage ./nix/package.nix { };
        in
        {
          "pipes-sh-python" = package;
          default = package;
        }
      );

      apps = forAllSystems (system: {
        pipes = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/pipes";
        };
        default = self.apps.${system}.pipes;
      });

      checks = forAllSystems (system: {
        package = self.packages.${system}.default;
      });

      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python3
              python3Packages.build
              python3Packages.installer
              python3Packages.setuptools
              python3Packages.wheel
              ruff
              nixfmt-rfc-style
              ncurses
              groff
            ];
          };
        }
      );
    };
}
