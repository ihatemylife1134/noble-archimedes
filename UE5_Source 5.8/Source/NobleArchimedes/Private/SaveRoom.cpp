// Fill out your copyright notice in the Description page of Project Settings.

#include "SaveRoom.h"
#include "HectorCharacter.h"
#include "NobleArchimedesGameInstance.h"
#include "Kismet/GameplayStatics.h"
#include "Components/BoxComponent.h"

// Sets default values
ASaveRoom::ASaveRoom()
{
	bIsSaveRoom = true;
	bIsLocked = false;
}

void ASaveRoom::BeginPlay()
{
	Super::BeginPlay();

	// Bind overlap event for player entry
	if (RoomTriggerBox)
	{
		RoomTriggerBox->OnComponentBeginOverlap.AddDynamic(this, &ASaveRoom::OnPlayerEnterSaveRoom);
	}
}

void ASaveRoom::ActivateSaveRoom(class AHectorCharacter* Player)
{
	if (!Player) return;

	// Full heal player and all Innocent Devils
	FullHealPlayer(Player);

	// Auto-save to slot
	if (bAutoSaveOnEntry)
	{
		if (UNobleArchimedesGameInstance* GameInstance = Cast<UNobleArchimedesGameInstance>(GetGameInstance()))
		{
			GameInstance->SaveGame(5); // Slot 5 = auto-save
		}
	}
}

void ASaveRoom::FullHealPlayer(class AHectorCharacter* Player)
{
	if (!Player) return;

	// Restore health to max
	Player->SetHealth(Player->GetMaxHealth());

	// Restore mana via combat component
	if (UNobleArchimedesCombatComponent* Combat = Player->CombatComponent)
	{
		Combat->SetHealth(Combat->GetMaxHealth());
		// Mana restoration would be handled here if mana system is expanded
	}

	// Heal all Innocent Devils
	TArray<FInnocentDevilData> Devils = Player->GetInnocentDevils();
	for (auto& Devil : Devils)
	{
		Devil.Health = Devil.MaxHealth;
	}
}

void ASaveRoom::OnPlayerEnterSaveRoom(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AHectorCharacter* Hector = Cast<AHectorCharacter>(OtherActor))
	{
		ActivateSaveRoom(Hector);
	}
}
