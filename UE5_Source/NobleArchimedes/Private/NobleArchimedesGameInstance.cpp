// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesGameInstance.h"
#include "NobleArchimedesSaveGame.h"
#include "HectorCharacter.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/Paths.h"

UNobleArchimedesGameInstance::UNobleArchimedesGameInstance()
{
}

FString UNobleArchimedesGameInstance::GetSaveSlotName(int32 SlotIndex) const
{
	return FString::Printf(TEXT("NobleArchimedes_Save_%d"), SlotIndex);
}

FString UNobleArchimedesGameInstance::GetSaveDirectory() const
{
	return FPaths::ProjectSavedDir() + TEXT("Saves/");
}

void UNobleArchimedesGameInstance::SaveGame(int32 SlotIndex)
{
	if (!CurrentSaveGame)
	{
		CurrentSaveGame = Cast<UNobleArchimedesSaveGame>(UGameplayStatics::CreateSaveGameObject(UNobleArchimedesSaveGame::StaticClass()));
	}

	// Capture current game state from world
	if (UWorld* World = GetWorld())
	{
		if (AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0)))
		{
			//=== PLAYER DATA ===
			CurrentSaveGame->PlayerName = Player->GetPlayerName();
			CurrentSaveGame->Health = Player->GetHealth();
			CurrentSaveGame->MaxHealth = Player->GetMaxHealth();
			CurrentSaveGame->Mana = Player->GetMana();
			CurrentSaveGame->MaxMana = Player->GetMaxMana();
			CurrentSaveGame->Level = Player->GetLevel();
			CurrentSaveGame->Experience = Player->GetExperience();
			CurrentSaveGame->SkillPoints = Player->GetSkillPoints();

			//=== TRANSFORM / LEVEL ===
			CurrentSaveGame->PlayerLocation = Player->GetActorLocation();
			CurrentSaveGame->PlayerRotation = Player->GetActorRotation();
			CurrentSaveGame->CurrentCameraMode = Player->GetCameraMode();
			CurrentSaveGame->CurrentLevelName = World->GetMapName();

			//=== INVENTORY & EQUIPMENT ===
			CurrentSaveGame->InventoryItems = Player->GetInventoryItems();
			CurrentSaveGame->EquippedWeapons = Player->GetEquippedWeapons();
			CurrentSaveGame->EquippedWeaponType = Player->GetEquippedWeaponType();

			//=== INNOCENT DEVILS ===
			CurrentSaveGame->InnocentDevils = Player->GetInnocentDevils();
			CurrentSaveGame->ActiveInnocentDevilIndex = Player->GetActiveInnocentDevilIndex();
			CurrentSaveGame->UnlockedInnocentDevils = Player->GetUnlockedInnocentDevils();

			//=== ITEMS ===
			CurrentSaveGame->bHasDeathDoll = Player->HasDeathDoll();

			//=== WEAPON FORGING ===
			CurrentSaveGame->DiscoveredRecipes = Player->GetDiscoveredRecipes();
			CurrentSaveGame->ForgedWeapons = Player->GetForgedWeapons();

			//=== SETTINGS ===
			CurrentSaveGame->MasterVolume = Player->GetMasterVolume();
			CurrentSaveGame->SFXVolume = Player->GetSFXVolume();
			CurrentSaveGame->MusicVolume = Player->GetMusicVolume();
		}
	}

	// Save to slot
	FString SlotName = GetSaveSlotName(SlotIndex);
	UGameplayStatics::SaveGameToSlot(CurrentSaveGame, SlotName, 0);
}

void UNobleArchimedesGameInstance::LoadGame(int32 SlotIndex)
{
	FString SlotName = GetSaveSlotName(SlotIndex);

	if (UGameplayStatics::DoesSaveGameExist(SlotName, 0))
	{
		CurrentSaveGame = Cast<UNobleArchimedesSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName, 0));

		// Apply all saved values to HectorCharacter and components if available.
		// Note: OpenLevel is asynchronous, so HectorCharacter may not exist yet.
		// Values are preserved in CurrentSaveGame and can be re-applied on BeginPlay if needed.
		if (UWorld* World = GetWorld())
		{
			if (AHectorCharacter* Player = Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0)))
			{
				//=== PLAYER DATA ===
				Player->SetPlayerName(CurrentSaveGame->PlayerName);
				Player->SetHealth(CurrentSaveGame->Health);
				Player->SetMaxHealth(CurrentSaveGame->MaxHealth);
				Player->SetMana(CurrentSaveGame->Mana);
				Player->SetMaxMana(CurrentSaveGame->MaxMana);
				Player->SetLevel(CurrentSaveGame->Level);
				Player->SetExperience(CurrentSaveGame->Experience);
				Player->SetSkillPoints(CurrentSaveGame->SkillPoints);

				//=== INVENTORY & EQUIPMENT ===
				Player->SetInventoryItems(CurrentSaveGame->InventoryItems);
				Player->SetEquippedWeaponType(CurrentSaveGame->EquippedWeaponType);
				if (Player->CombatComponent)
				{
					Player->CombatComponent->SetEquippedWeapons(CurrentSaveGame->EquippedWeapons);
				}

				//=== ITEMS ===
				Player->SetDeathDoll(CurrentSaveGame->bHasDeathDoll);

				//=== CAMERA ===
				Player->SetCameraMode(CurrentSaveGame->CurrentCameraMode);
			}
		}

		// Load the saved level
		if (!CurrentSaveGame->CurrentLevelName.IsEmpty())
		{
			UGameplayStatics::OpenLevel(GetWorld(), FName(*CurrentSaveGame->CurrentLevelName));
		}
	}
}

bool UNobleArchimedesGameInstance::HasSaveGame(int32 SlotIndex) const
{
	return UGameplayStatics::DoesSaveGameExist(GetSaveSlotName(SlotIndex), 0);
}

void UNobleArchimedesGameInstance::DeleteSaveGame(int32 SlotIndex)
{
	UGameplayStatics::DeleteGameInSlot(GetSaveSlotName(SlotIndex), 0);
}

TArray<FString> UNobleArchimedesGameInstance::GetSaveSlotNames() const
{
	TArray<FString> Names;
	for (int32 i = 0; i < MaxSaveSlots; i++)
	{
		Names.Add(GetSaveSlotName(i));
	}
	return Names;
}