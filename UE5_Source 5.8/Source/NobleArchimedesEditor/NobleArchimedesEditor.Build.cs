// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class NobleArchimedesEditor : ModuleRules
{
	public NobleArchimedesEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
		});

		// AnimGraph is an editor-only module, which is why this module is an
		// Editor module: the state machine graph internals it exposes are not
		// reachable from script.
		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"UnrealEd",
			"AnimGraph",
			"AnimGraphRuntime",
			"AnimationBlueprintLibrary",
			"BlueprintGraph",
			"Kismet",
			"KismetCompiler",
			"EditorFramework",
			"GraphEditor",
		});
	}
}
