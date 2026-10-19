// Fill out your copyright notice in the Description page of Project Settings.

using UnrealBuildTool;

public class NobleArchimedes : ModuleRules
{
	public NobleArchimedes(ReadOnlyTargetRules Target) : base(Target)
	{
		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"NavigationSystem",
			"AIModule",
			"GameplayTasks",
			"LevelStreaming",
			"Niagara"
		});

		PrivateDependencyModuleNames.AddRange(new string[] {
		});

		DynamicallyLoadedModuleNames.AddRange(new string[] {
		});
	}
}