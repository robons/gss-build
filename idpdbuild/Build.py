from waflib.Build import BuildContext


def build(bld: BuildContext):
    print(f"Building with context in {bld.top_dir}")
    