// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NobleInputBuilder.generated.h"

class UInputAction;
class UInputMappingContext;

/**
 * Small authoring helper used by the content pipeline to build Enhanced Input
 * mapping contexts. FKey is not constructible from Python, so this bridges the
 * gap and keeps mapping setup reproducible.
 */
UCLASS()
class NOBLEARCHIMEDES_API UNobleInputBuilder : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Appends a key mapping to Context.
	 *
	 * @param KeyName   FKey name, e.g. "W", "Mouse2D", "Gamepad_Left2D".
	 * @param bNegateX  Invert the X axis of the resulting action value.
	 * @param bNegateY  Invert the Y axis of the resulting action value.
	 * @param bSwizzleYXZ Move a 1D key value onto the Y axis (for Axis2D actions).
	 */
	UFUNCTION(BlueprintCallable, Category = "Input|Authoring")
	static void AddKeyMapping(UInputMappingContext* Context, UInputAction* Action, FName KeyName,
		bool bNegateX = false, bool bNegateY = false, bool bSwizzleYXZ = false);

	/** Removes every mapping from Context. */
	UFUNCTION(BlueprintCallable, Category = "Input|Authoring")
	static void ClearMappings(UInputMappingContext* Context);

	/** Number of key mappings authored on a context.

	 * Mappings is protected and the Python get_mappings() call returns an empty
	 * array for this build, so verification tools had no way to confirm that an
	 * input context is actually populated. */
	UFUNCTION(BlueprintCallable, Category = "Input|Authoring")
	static int32 GetMappingCount(UInputMappingContext* Context);

	/** Names of the actions mapped on a context, for verification tools. */
	UFUNCTION(BlueprintCallable, Category = "Input|Authoring")
	static TArray<FName> GetMappedActionNames(UInputMappingContext* Context);
};
