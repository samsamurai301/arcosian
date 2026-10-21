#!/usr/bin/env python3
"""Build a plain .NET test project around Game.Core and the EditMode tests (no Unity licence needed).

Usage: python3 build_harness.py <unity-project-dir> <output-dir>
Then:  cd <output-dir>/Tests && UNITY_ASSETS_DIR=<unity-project-dir>/Assets dotnet test
       (NUnit 3.14.0, NUnit3TestAdapter and Microsoft.NET.Test.Sdk are pinned in the generated Tests.csproj.)
Core compiles as netstandard2.1 with LangVersion 9.0 (Unity's C# level); tests run on net10.0.
"""
import re, sys, pathlib
if len(sys.argv) != 3:
    sys.exit(__doc__)
tmpl, h = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2])
(h/'Core').mkdir(parents=True, exist_ok=True); (h/'Tests').mkdir(parents=True, exist_ok=True)
core = f'''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.1</TargetFramework>
    <LangVersion>9.0</LangVersion>
    <Nullable>disable</Nullable>
    <AssemblyName>Game.Core</AssemblyName>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="{tmpl}/Assets/_Game/Core/**/*.cs" />
  </ItemGroup>
</Project>
'''
(h/"Core/Core.csproj").write_text(core, encoding="utf-8")
src = (tmpl/"Assets/_Game/Presentation/SwipeInput.cs").read_text(encoding="utf-8")
i = src.index("public static string Classify(")
j = src.index("{", i); depth = 0; k = j
while True:
    if src[k] == "{": depth += 1
    elif src[k] == "}":
        depth -= 1
        if depth == 0: break
    k += 1
method = src[i:k+1]
stubs = '''// Minimal stand-ins for the three Unity types the EditMode tests touch. Generated; do not edit.
namespace UnityEngine
{
    public static class Application { public static string dataPath = System.Environment.GetEnvironmentVariable("UNITY_ASSETS_DIR"); }
    public struct Vector2
    {
        public float x, y;
        public Vector2(float x, float y) { this.x = x; this.y = y; }
        public float magnitude => (float)System.Math.Sqrt(x * x + y * y);
    }
    public static class Mathf { public static float Abs(float f) => System.Math.Abs(f); }
}
namespace Game.Presentation
{
    using UnityEngine;
    // Classify is copied verbatim from Assets/_Game/Presentation/SwipeInput.cs at harness build time.
    public static class SwipeInput
    {
        ''' + method + '''
    }
}
'''
(h/"Tests/Stubs.cs").write_text(stubs, encoding="utf-8")
tests = f'''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <LangVersion>9.0</LangVersion>
    <Nullable>disable</Nullable>
    <IsPackable>false</IsPackable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="{tmpl}/Assets/_Game/Tests/EditMode/*.cs" />
    <Compile Include="Stubs.cs" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="../Core/Core.csproj" />
    <PackageReference Include="NUnit" Version="3.14.0" />
    <PackageReference Include="NUnit3TestAdapter" Version="6.3.1" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="18.11.0" />
  </ItemGroup>
</Project>
'''
(h/"Tests/Tests.csproj").write_text(tests, encoding="utf-8")
print("harness written; Classify extracted (%d chars)" % len(method))
