// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NobleDataTableAuthoring.generated.h"

class UDataTable;

/**
 * Script-callable helpers for editing weapon data table rows in place.
 *
 * The combat component reads its attack montages from FWeaponData rows
 * (ComboAnimations for light stages, FinalAttackAnimations for the finisher), and
 * the content pipeline only ever writes those two arrays while rebuilding the
 * whole table from CSV. Retargeting the character onto a new skeleton left those
 * arrays pointing at montages bound to the old skeleton, which the new mesh
 * cannot play, so they have to be repointed without disturbing any other field.
 *
 * Round-tripping the table through JSON would work but requires reproducing the
 * pipeline's whole CSV conversion (parse_value, RENAMES, per-field coercion), and
 * any field it fails to reproduce is silently reset to its default. Editing the
 * row struct directly touches only the two arrays.
 */
UCLASS()
class NOBLEARCHIMEDESEDITOR_API UNobleDataTableAuthoring : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Replaces a weapon row's attack montage arrays.
	 *
	 * Paths are content paths (e.g. "/Game/Characters/HectorBase/Montages/AM_HectorBase_Light1").
	 * Paths that fail to load are reported in the returned string rather than
	 * silently dropped, so a typo cannot masquerade as a successful edit.
	 * Returns an empty string on success, or a description of what went wrong.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|DataTable")
	static FString SetWeaponRowMontages(UDataTable* Table, FName RowName,
		const TArray<FString>& ComboMontagePaths,
		const TArray<FString>& FinalMontagePaths);

	/**
	 * Reports a row's current montage assignments and the skeleton each is bound
	 * to, so a repoint can be verified rather than assumed.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|DataTable")
	static FString DescribeWeaponRowMontages(UDataTable* Table, FName RowName);

	/** Reports every row name in the table. */
	UFUNCTION(BlueprintCallable, Category = "Noble|DataTable")
	static TArray<FName> GetRowNames(UDataTable* Table);
};
