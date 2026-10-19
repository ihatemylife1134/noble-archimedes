// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;

public class NobleArchimedes : ModuleRules
{
	public NobleArchimedes(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode::UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"HeadMountedDisplay",
			"NavigationSystem",
			"AIModule",
			"GameplayTasks",
			"LevelStreaming"
		});

		PrivateDependencyModuleNames.AddRange(new string[] {
		});

		DynamicallyLoadedModuleNames.AddRange(new string[] {
		});
	}
}