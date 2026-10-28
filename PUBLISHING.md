# Publishing a version

1. Create a publisher profile at https://registry.comfy.org/.
2. Add its exact `PublisherId` to `[tool.comfy]` in `pyproject.toml`.
3. Bump `project.version` for each release and run the checks.
4. Create a Registry publishing key in that publisher's settings.
5. Run `comfy node publish` with the official Comfy CLI; enter the key when prompted.

Do not put the publishing key in source files. The repository metadata is ready
for the publisher ID; creating the GitHub repository does not register a package
in the Comfy Registry automatically. Keep both packages under the same publisher
if they are maintained together.

Official instructions: https://docs.comfy.org/registry/publishing
