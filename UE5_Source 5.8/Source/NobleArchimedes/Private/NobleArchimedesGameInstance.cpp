// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesGameInstance.h"
#include "NobleArchimedesSaveGame.h"
#include "NobleArchimedesGameModeBase.h"
#include "NobleArchimedesItemSystem.h"
#include "NobleArchimedesWeaponForge.h"
#include "HectorCharacter.h"
#include "Engine/World.h"
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

TMap<FName, int32> UNobleArchimedesGameInstance::InventoryArrayToMap(const TArray<FInventoryItem>& Items) const
{
	TMap<FName, int32> Result;
	for (const FInventoryItem& Item : Items)
	{
		if (!Item.ItemName.IsNone() && Item.Quantity > 0)
		{
			Result.FindOrAdd(Item.ItemName) += Item.Quantity;
		}
	}
	return Result;
}

TArray<FInventoryItem> UNobleArchimedesGameInstance::InventoryMapToArray(const TMap<FName, int32>& Items) const
{
	TArray<FInventoryItem> Result;
	Result.Reserve(Items.Num());
	for (const auto& Pair : Items)
	{
		if (Pair.Key.IsNone() || Pair.Value <= 0)
		{
			continue;
		}

		FInventoryItem Item;
		Item.ItemName = Pair.Key;
		Item.Quantity = Pair.Value;
		Result.Add(Item);
	}
	return Result;
}

void UNobleArchimedesGameInstance::SaveGame(int32 SlotIndex)
{
	if (!CurrentSaveGame)
	{
		CurrentSaveGame = Cast<UNobleArchimedesSaveGame>(
			UGameplayStatics::CreateSaveGameObject(UNobleArchimedesSaveGame::StaticClass()));
	}
	if (!CurrentSaveGame)
	{
		UE_LOG(LogTemp, Error, TEXT("NobleArchimedes: failed to create a save game object."));
		return;
	}

	UWorld* World = GetWorld();
	AHectorCharacter* Player = World
		? Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0))
		: nullptr;
	if (!Player || !World)
	{
		UE_LOG(LogTemp, Warning, TEXT("NobleArchimedes: SaveGame called without a player."));
		return;
	}

	CurrentSaveGame->PlayerName = Player->GetPlayerName();
	CurrentSaveGame->Health = FMath::RoundToInt(Player->GetHealth());
	CurrentSaveGame->MaxHealth = FMath::RoundToInt(Player->GetMaxHealth());
	CurrentSaveGame->Mana = FMath::RoundToInt(Player->GetMana());
	CurrentSaveGame->MaxMana = FMath::RoundToInt(Player->GetMaxMana());
	CurrentSaveGame->Level = Player->GetCharacterLevel();
	CurrentSaveGame->Experience = Player->GetExperience();
	CurrentSaveGame->SkillPoints = Player->GetSkillPoints();

	CurrentSaveGame->PlayerLocation = Player->GetActorLocation();
	CurrentSaveGame->PlayerRotation = Player->GetActorRotation();
	CurrentSaveGame->CurrentCameraMode = Player->GetCameraMode();
	CurrentSaveGame->CurrentLevelName = UGameplayStatics::GetCurrentLevelName(World, true);

	if (UNobleArchimedesItemSystem* ItemSystem = Player->GetItemSystem())
	{
		CurrentSaveGame->InventoryItems = InventoryMapToArray(ItemSystem->GetAllItems());
		CurrentSaveGame->bHasDeathDoll =
			ItemSystem->GetItemQuantity(TEXT("Death Doll")) > 0 || Player->HasDeathDoll();
	}
	else
	{
		CurrentSaveGame->InventoryItems = Player->GetInventoryItems();
		CurrentSaveGame->bHasDeathDoll = Player->HasDeathDoll();
	}

	if (UNobleArchimedesWeaponForge* Forge = Player->GetWeaponForge())
	{
		CurrentSaveGame->ForgeMaterials = InventoryMapToArray(Forge->GetAllMaterialQuantities());
		CurrentSaveGame->DiscoveredRecipes = Forge->GetDiscoveredRecipes();
		CurrentSaveGame->ForgedWeapons = Forge->GetForgedWeapons();
	}
	else
	{
		CurrentSaveGame->DiscoveredRecipes = Player->GetDiscoveredRecipes();
		CurrentSaveGame->ForgedWeapons = Player->GetForgedWeapons();
	}

	CurrentSaveGame->EquippedWeapons = Player->GetEquippedWeapons();
	CurrentSaveGame->EquippedWeaponType = Player->GetEquippedWeaponType();
	CurrentSaveGame->InnocentDevils = Player->GetInnocentDevils();
	CurrentSaveGame->ActiveInnocentDevilIndex = Player->GetActiveInnocentDevilIndex();
	CurrentSaveGame->UnlockedInnocentDevils = Player->GetUnlockedInnocentDevils();

	CurrentSaveGame->MasterVolume = Player->GetMasterVolume();
	CurrentSaveGame->SFXVolume = Player->GetSFXVolume();
	CurrentSaveGame->MusicVolume = Player->GetMusicVolume();

	if (ANobleArchimedesGameModeBase* GameMode = Cast<ANobleArchimedesGameModeBase>(World->GetAuthGameMode()))
	{
		CurrentSaveGame->CurrentChapter = GameMode->GetCurrentChapter();
		CurrentSaveGame->CompletedChapters = GameMode->GetCompletedChapters();
		CurrentSaveGame->UnlockedWeaponRecipes = GameMode->GetUnlockedWeaponRecipes();
	}

	const FString SlotName = GetSaveSlotName(SlotIndex);
	const bool bSaved = UGameplayStatics::SaveGameToSlot(CurrentSaveGame, SlotName, 0);
	UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: SaveGame slot=%d level=%s success=%s."),
		SlotIndex, *CurrentSaveGame->CurrentLevelName, bSaved ? TEXT("true") : TEXT("false"));
}

void UNobleArchimedesGameInstance::LoadGame(int32 SlotIndex)
{
	const FString SlotName = GetSaveSlotName(SlotIndex);
	if (!UGameplayStatics::DoesSaveGameExist(SlotName, 0))
	{
		UE_LOG(LogTemp, Warning, TEXT("NobleArchimedes: no save in slot %d."), SlotIndex);
		return;
	}

	USaveGame* Loaded = UGameplayStatics::LoadGameFromSlot(SlotName, 0);
	CurrentSaveGame = Cast<UNobleArchimedesSaveGame>(Loaded);
	if (!CurrentSaveGame)
	{
		UE_LOG(LogTemp, Error, TEXT("NobleArchimedes: save slot %d has the wrong save class."), SlotIndex);
		return;
	}

	bPendingLoad = true;
	UWorld* World = GetWorld();
	const FString CurrentLevel = World
		? UGameplayStatics::GetCurrentLevelName(World, true)
		: FString();
	if (World && !CurrentSaveGame->CurrentLevelName.IsEmpty() &&
		!CurrentLevel.Equals(CurrentSaveGame->CurrentLevelName, ESearchCase::IgnoreCase))
	{
		UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: loading save slot %d, opening level %s."),
			SlotIndex, *CurrentSaveGame->CurrentLevelName);
		UGameplayStatics::OpenLevel(World, FName(*CurrentSaveGame->CurrentLevelName));
		return;
	}

	ApplyPendingLoad();
}

void UNobleArchimedesGameInstance::ApplyPendingLoad()
{
	if (!bPendingLoad || !CurrentSaveGame)
	{
		return;
	}

	UWorld* World = GetWorld();
	AHectorCharacter* Player = World
		? Cast<AHectorCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0))
		: nullptr;
	if (!Player)
	{
		// The player pawn is created after GameInstance::LoadGame during a
		// level transition. HectorCharacter::BeginPlay retries this call.
		return;
	}

	ApplySaveGameToPlayer(Player);
	bPendingLoad = false;
	UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: save applied. Level=%s Health=%.1f."),
		*CurrentSaveGame->CurrentLevelName, Player->GetHealth());
}

void UNobleArchimedesGameInstance::ApplySaveGameToPlayer(AHectorCharacter* Player)
{
	if (!CurrentSaveGame || !Player)
	{
		return;
	}

	const UNobleArchimedesSaveGame& Save = *CurrentSaveGame;

	Player->SetPlayerName(Save.PlayerName);
	Player->SetMaxHealth(static_cast<float>(FMath::Max(1, Save.MaxHealth)));
	Player->SetHealth(static_cast<float>(Save.Health));
	Player->SetMaxMana(static_cast<float>(FMath::Max(0, Save.MaxMana)));
	Player->SetMana(static_cast<float>(Save.Mana));
	Player->SetLevel(Save.Level);
	Player->SetExperience(Save.Experience);
	Player->SetSkillPoints(Save.SkillPoints);

	if (UNobleArchimedesItemSystem* ItemSystem = Player->GetItemSystem())
	{
		ItemSystem->SetAllItems(InventoryArrayToMap(Save.InventoryItems));
		if (Save.bHasDeathDoll && ItemSystem->GetItemQuantity(TEXT("Death Doll")) <= 0)
		{
			ItemSystem->AddItem(TEXT("Death Doll"), 1);
		}
	}
	else
	{
		Player->SetInventoryItems(Save.InventoryItems);
	}

	if (UNobleArchimedesWeaponForge* Forge = Player->GetWeaponForge())
	{
		Forge->SetAllMaterialQuantities(InventoryArrayToMap(Save.ForgeMaterials));
		Forge->SetDiscoveredRecipes(Save.DiscoveredRecipes);
		Forge->SetForgedWeapons(Save.ForgedWeapons);
	}

	Player->SetDiscoveredRecipes(Save.DiscoveredRecipes);
	Player->SetForgedWeapons(Save.ForgedWeapons);

	Player->SetEquippedWeaponType(Save.EquippedWeaponType);
	if (Player->CombatComponent)
	{
		Player->CombatComponent->SetEquippedWeapons(Save.EquippedWeapons);
	}

	Player->SetInnocentDevils(Save.InnocentDevils);
	Player->SetUnlockedInnocentDevils(Save.UnlockedInnocentDevils);
	Player->SetActiveInnocentDevilIndex(Save.ActiveInnocentDevilIndex);

	Player->SetDeathDoll(Save.bHasDeathDoll);
	Player->SetCameraMode(Save.CurrentCameraMode);

	if (!Save.PlayerLocation.IsNearlyZero())
	{
		Player->SetActorLocationAndRotation(
			Save.PlayerLocation, Save.PlayerRotation, false, nullptr,
			ETeleportType::TeleportPhysics);
	}

	if (UWorld* World = GetWorld())
	{
		if (ANobleArchimedesGameModeBase* GameMode =
			Cast<ANobleArchimedesGameModeBase>(World->GetAuthGameMode()))
		{
			GameMode->RestoreProgressFromSave(CurrentSaveGame);
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
