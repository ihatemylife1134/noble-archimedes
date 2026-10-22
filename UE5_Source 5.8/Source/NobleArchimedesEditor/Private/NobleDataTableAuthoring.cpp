// Copyright Epic Games, Inc. All Rights Reserved.

#include "NobleDataTableAuthoring.h"

#include "Animation/AnimMontage.h"
#include "Engine/DataTable.h"
#include "NobleArchimedesTypes.h"

namespace
{
	/** Loads montage paths, collecting any that fail so the caller can report them. */
	TArray<UAnimMontage*> ResolveMontages(const TArray<FString>& Paths, TArray<FString>& OutMissing)
	{
		TArray<UAnimMontage*> Resolved;
		Resolved.Reserve(Paths.Num());

		for (const FString& Path : Paths)
		{
			if (Path.IsEmpty())
			{
				continue;
			}

			UAnimMontage* Montage = LoadObject<UAnimMontage>(nullptr, *Path);
			if (Montage)
			{
				Resolved.Add(Montage);
			}
			else
			{
				OutMissing.Add(Path);
			}
		}
		return Resolved;
	}

	FString DescribeMontage(const UAnimMontage* Montage)
	{
		if (!Montage)
		{
			return TEXT("<null>");
		}

		const USkeleton* Skeleton = Montage->GetSkeleton();
		return FString::Printf(TEXT("%s [%s]"), *Montage->GetName(),
			Skeleton ? *Skeleton->GetName() : TEXT("no skeleton"));
	}
}

FString UNobleDataTableAuthoring::SetWeaponRowMontages(UDataTable* Table, FName RowName,
	const TArray<FString>& ComboMontagePaths, const TArray<FString>& FinalMontagePaths)
{
	if (!Table)
	{
		return TEXT("no table supplied");
	}

	FWeaponData* Row = Table->FindRow<FWeaponData>(RowName, TEXT("SetWeaponRowMontages"), false);
	if (!Row)
	{
		return FString::Printf(TEXT("row '%s' not found"), *RowName.ToString());
	}

	TArray<FString> Missing;
	const TArray<UAnimMontage*> Combo = ResolveMontages(ComboMontagePaths, Missing);
	const TArray<UAnimMontage*> Final = ResolveMontages(FinalMontagePaths, Missing);

	// Assign even when a path failed, so the row never keeps a montage bound to
	// the old skeleton -- that is the bug this exists to fix.
	Table->Modify();
	Row->ComboAnimations = Combo;
	Row->FinalAttackAnimations = Final;
	Table->MarkPackageDirty();

	if (Missing.Num() > 0)
	{
		return FString::Printf(TEXT("applied with %d unresolved path(s): %s"),
			Missing.Num(), *FString::Join(Missing, TEXT(", ")));
	}
	return FString();
}

FString UNobleDataTableAuthoring::DescribeWeaponRowMontages(UDataTable* Table, FName RowName)
{
	if (!Table)
	{
		return TEXT("no table supplied");
	}

	const FWeaponData* Row = Table->FindRow<FWeaponData>(RowName, TEXT("DescribeWeaponRowMontages"), false);
	if (!Row)
	{
		return FString::Printf(TEXT("row '%s' not found"), *RowName.ToString());
	}

	TArray<FString> Combo;
	for (const UAnimMontage* Montage : Row->ComboAnimations)
	{
		Combo.Add(DescribeMontage(Montage));
	}

	TArray<FString> Final;
	for (const UAnimMontage* Montage : Row->FinalAttackAnimations)
	{
		Final.Add(DescribeMontage(Montage));
	}

	return FString::Printf(TEXT("combo[%d]=%s final[%d]=%s"),
		Combo.Num(), *FString::Join(Combo, TEXT(" | ")),
		Final.Num(), *FString::Join(Final, TEXT(" | ")));
}

TArray<FName> UNobleDataTableAuthoring::GetRowNames(UDataTable* Table)
{
	return Table ? Table->GetRowNames() : TArray<FName>();
}
