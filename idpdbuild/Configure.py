from waflib.Configure import ConfigurationContext


def configure(ctx: ConfigurationContext):
    print(f"Configuring with context in {ctx.top_dir}")