// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesGameModeBase.h"
#include "NobleArchimedesSaveGame.h"
#include "NobleArchimedesGameInstance.h"
#include "HectorCharacter.h"
#include "Engine/DataTable.h"
#include "Kismet/GameplayStatics.h"

ANobleArchimedesGameModeBase::ANobleArchimedesGameModeBase()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ANobleArchimedesGameModeBase::BeginPlay()
{
	Super::BeginPlay();

	GameInstance = Cast<UNobleArchimedesGameInstance>(GetGameInstance());
	SaveGameInstance = Cast<UNobleArchimedesSaveGame>(UGameplayStatics::CreateSaveGameObject(UNobleArchimedesSaveGame::StaticClass()));

	InitializeGameState();

	// When a chapter portal saves and opens the next level, the save game stays
	// alive on the GameInstance. Restore the chapter and unlocks here without
	// applying the old level's player transform.
	if (GameInstance && GameInstance->GetCurrentSaveGame())
	{
		const UNobleArchimedesSaveGame* Save = GameInstance->GetCurrentSaveGame();
		CurrentChapter = Save->CurrentChapter;
		CompletedChapters = Save->CompletedChapters;
		UnlockedInnocentDevils = Save->UnlockedInnocentDevils;
		UnlockedWeaponRecipes = Save->UnlockedWeaponRecipes;
	}

	ApplyChapterUnlocks(CurrentChapter);
}

namespace
{
	EInnocentDevilType DevilTypeFromDisplayName(FName Name)
	{
		if (Name == TEXT("Fairy")) return EInnocentDevilType::Fairy;
		if (Name == TEXT("Griffin")) return EInnocentDevilType::Griffin;
		if (Name == TEXT("Salamander")) return EInnocentDevilType::Salamander;
		if (Name == TEXT("Ogre")) return EInnocentDevilType::Ogre;
		if (Name == TEXT("Skeleton Devil") || Name == TEXT("Skeleton"))
			return EInnocentDevilType::Skeleton;
		if (Name == TEXT("Witch Devil") || Name == TEXT("Witch"))
			return EInnocentDevilType::Witch;
		if (Name == TEXT("Pumpkin")) return EInnocentDevilType::Pumpkin;
		return EInnocentDevilType::None;
	}
}

void ANobleArchimedesGameModeBase::InitializeGameState()
{
	CurrentChapter = 1;
	CompletedChapters.Empty();
	UnlockedInnocentDevils.Empty();
	UnlockedWeaponRecipes.Empty();

	// Always unlocked: Short Sword
	UnlockedWeaponRecipes.Add("Short Sword");

	// A new session starts at Chapter 1. Continue/load is driven by the
	// GameInstance so the destination level can finish streaming before the
	// saved transform and inventory are applied.
}

void ANobleArchimedesGameModeBase::StartChapter(int32 ChapterIndex)
{
	CurrentChapter = ChapterIndex;
	ApplyChapterUnlocks(ChapterIndex);

	if (GameInstance)
	{
		GameInstance->SaveGame(0);
	}
}

void ANobleArchimedesGameModeBase::ApplyChapterUnlocks(int32 ChapterIndex)
{
	if (ChapterProgressionTable)
	{
		const FName RowName(*FString::FromInt(ChapterIndex));
		if (const FChapterProgression* Row =
			ChapterProgressionTable->FindRow<FChapterProgression>(
				RowName, TEXT("ApplyChapterUnlocks"), false))
		{
			const EInnocentDevilType DevilType =
				DevilTypeFromDisplayName(Row->InnocentDevilAcquired);
			if (DevilType != EInnocentDevilType::None)
			{
				UnlockedInnocentDevils.AddUnique(DevilType);
			}
			if (!Row->WeaponUnlocked.IsNone())
			{
				UnlockedWeaponRecipes.AddUnique(Row->WeaponUnlocked);
			}
		}
	}

	if (AHectorCharacter* Player = Cast<AHectorCharacter>(
		UGameplayStatics::GetPlayerCharacter(this, 0)))
	{
		Player->SetUnlockedInnocentDevils(UnlockedInnocentDevils);
	}
}

void ANobleArchimedesGameModeBase::CompleteChapter(int32 ChapterIndex)
{
	if (!CompletedChapters.Contains(ChapterIndex))
	{
		CompletedChapters.Add(ChapterIndex);
	}

	if (GameInstance)
	{
		GameInstance->SaveGame(0);
	}
}

bool ANobleArchimedesGameModeBase::IsChapterCompleted(int32 ChapterIndex) const
{
	return CompletedChapters.Contains(ChapterIndex);
}

void ANobleArchimedesGameModeBase::SaveGameProgress()
{
	if (GameInstance)
	{
		GameInstance->SaveGame(0);
	}
}

void ANobleArchimedesGameModeBase::LoadGameProgress(int32 SlotIndex)
{
	if (GameInstance)
	{
		GameInstance->LoadGame(SlotIndex);

		if (GameInstance->GetCurrentSaveGame())
		{
			RestoreProgressFromSave(GameInstance->GetCurrentSaveGame());
		}
	}
}

void ANobleArchimedesGameModeBase::RestoreProgressFromSave(const UNobleArchimedesSaveGame* Save)
{
	if (!Save)
	{
		return;
	}

	CurrentChapter = Save->CurrentChapter;
	CompletedChapters = Save->CompletedChapters;
	UnlockedInnocentDevils = Save->UnlockedInnocentDevils;
	UnlockedWeaponRecipes = Save->UnlockedWeaponRecipes;
	if (UnlockedWeaponRecipes.Num() == 0)
	{
		UnlockedWeaponRecipes = Save->ForgedWeapons;
	}
	if (!UnlockedWeaponRecipes.Contains("Short Sword"))
	{
		UnlockedWeaponRecipes.Add("Short Sword");
	}
}

void ANobleArchimedesGameModeBase::AutoSave()
{
	if (GameInstance)
	{
		GameInstance->SaveGame(GameInstance->AutoSaveSlot);
	}
}

void ANobleArchimedesGameModeBase::UnlockInnocentDevil(EInnocentDevilType Type)
{
	if (!UnlockedInnocentDevils.Contains(Type))
	{
		UnlockedInnocentDevils.Add(Type);

		if (GameInstance)
		{
			GameInstance->SaveGame(0);
		}
	}
}

bool ANobleArchimedesGameModeBase::IsInnocentDevilUnlocked(EInnocentDevilType Type) const
{
	return UnlockedInnocentDevils.Contains(Type);
}

void ANobleArchimedesGameModeBase::UnlockWeaponRecipe(FName WeaponName)
{
	if (!UnlockedWeaponRecipes.Contains(WeaponName))
	{
		UnlockedWeaponRecipes.Add(WeaponName);

		if (GameInstance)
		{
			GameInstance->SaveGame(0);
		}
	}
}

bool ANobleArchimedesGameModeBase::IsWeaponRecipeUnlocked(FName WeaponName) const
{
	return UnlockedWeaponRecipes.Contains(WeaponName);
}

void ANobleArchimedesGameModeBase::LoadSaveData(int32 SlotIndex)
{
	if (GameInstance && GameInstance->GetCurrentSaveGame())
	{
		CurrentChapter = GameInstance->GetCurrentSaveGame()->CurrentChapter;
		CompletedChapters = GameInstance->GetCurrentSaveGame()->CompletedChapters;
		UnlockedInnocentDevils = GameInstance->GetCurrentSaveGame()->UnlockedInnocentDevils;
		UnlockedWeaponRecipes = GameInstance->GetCurrentSaveGame()->ForgedWeapons;
	}
}

void ANobleArchimedesGameModeBase::SaveCurrentState()
{
	if (GameInstance && GameInstance->GetCurrentSaveGame())
	{
		GameInstance->GetCurrentSaveGame()->CurrentChapter = CurrentChapter;
		GameInstance->GetCurrentSaveGame()->CompletedChapters = CompletedChapters;
		GameInstance->GetCurrentSaveGame()->UnlockedInnocentDevils = UnlockedInnocentDevils;
		GameInstance->GetCurrentSaveGame()->ForgedWeapons = UnlockedWeaponRecipes;

		GameInstance->SaveGame(0);
	}
}