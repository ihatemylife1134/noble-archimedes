// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesGameInstance.h"
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
		if (ANobleArchimedesCharacter* Player = Cast<ANobleArchimedesCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0)))
		{
			CurrentSaveGame->PlayerLocation = Player->GetActorLocation();
			CurrentSaveGame->PlayerRotation = Player->GetActorRotation();
			CurrentSaveGame->CurrentCameraMode = Player->GetCameraMode();
			CurrentSaveGame->Health = Player->GetHealth();
			CurrentSaveGame->MaxHealth = Player->GetMaxHealth();
			CurrentSaveGame->CurrentLevelName = World->GetMapName();
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