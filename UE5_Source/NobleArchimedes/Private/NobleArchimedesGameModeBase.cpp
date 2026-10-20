// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesGameModeBase.h"
#include "NobleArchimedesSaveGame.h"
#include "NobleArchimedesGameInstance.h"
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

	if (GameInstance)
	{
		GameInstance->SaveGame(0);
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