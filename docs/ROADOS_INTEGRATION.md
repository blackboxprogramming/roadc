# Edit RoadC source in RoadOS

RoadOS Code now has a local Git adapter for registered clones. This connects
RoadC source to the RoadOS workspace without changing the RoadC interpreter or
compiler.

## Setup

Run RoadOS from the `blackboxprogramming/0` repository with Node 24 and Git.
Register this clone by its actual absolute root path in the RoadOS host setting:

```sh
export ROAD_REPOSITORIES='[{"id":"roadc","label":"RoadC","path":"/absolute/path/to/roadc"}]'
npm run local
```

In RoadOS, open Code → Repositories → Load local repositories. Select RoadC,
search for `examples/`, and preview a committed file. Import into workspace saves
a source copy and a manifest containing the original commit, blob ID and path.
The clone is not modified. Unsaved or untracked checkout files are not imported.

## Language boundary

RoadC uses Python-style functions, expressions and control flow. RoadOS also has
a small workspace command dialect using `note`, `task`, `open` and assertions.
A shared `.road` extension does not make these runtimes interchangeable.
Imported RoadC source opens as plain text in Code; it is not granted workspace
execution permission. Use RoadC's documented local interpreter/compiler to run
RoadC programs. This integration does not launch that interpreter from RoadOS.

The adapter supports committed UTF-8 regular files up to 200 KB. It rejects
symlinks, binary files and Git LFS pointers. Code edits stay in the browser
workspace; export a file before deliberately applying edits back to this clone.

Full setup and endpoint contract:
[RoadOS repository integration](https://github.com/blackboxprogramming/0/blob/main/docs/repository-integration.md).

This repository's license and source notices remain unchanged. The connection
is source import, not a claim that every RoadC example compiles or that the two
language implementations are identical.
