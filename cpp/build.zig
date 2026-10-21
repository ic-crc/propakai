const std = @import("std");

pub fn build(b: *std.Build) void {
    const sub_projects = &.{
        "ntia_p368_10",
        "ntia_p528_5",
        "propakai_cpp",
    };

    inline for (sub_projects) |sub| {
        const cmd = b.addSystemCommand(&.{
            "zig",          "build",
            "--build-file", sub ++ "/build.zig",
        });
        b.getInstallStep().dependOn(&cmd.step);
    }
}
