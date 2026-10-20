// Fill out your copyright notice in the Description page of Project Settings.

#include "ItemDrop.h"
#include "HectorCharacter.h"
#include "NobleArchimedesItemSystem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"

// Sets default values
AItemDrop::AItemDrop()
{
	PrimaryActorTick.bCanEverTick = false;

	ItemMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ItemMesh"));
	RootComponent = ItemMesh;

	PickupTrigger = CreateDefaultSubobject<UBoxComponent>(TEXT("PickupTrigger"));
	PickupTrigger->SetupAttachment(ItemMesh);
	PickupTrigger->SetBoxExtent(FVector(50.0f, 50.0f, 50.0f));
	PickupTrigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	PickupTrigger->SetCollisionResponseToAllChannels(ECollisionResponse::ECR_Ignore);
	PickupTrigger->SetCollisionResponseToChannel(ECollisionChannel::ECC_Pawn, ECollisionResponse::ECR_Overlap);

	bIsStealOnly = false;
	bIsRare = false;
	AutoDestroyTime = 30.0f;
}

void AItemDrop::BeginPlay()
{
	Super::BeginPlay();

	PickupTrigger->OnComponentBeginOverlap.AddDynamic(this, &AItemDrop::OnPlayerEnterPickup);

	// Auto-destroy after time limit
	GetWorld()->GetTimerManager().SetTimer(AutoDestroyTimerHandle, this, &AItemDrop::AutoDestroy, AutoDestroyTime, false);
}

void AItemDrop::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void AItemDrop::InitializeItem(FName NewItemName, bool NewIsStealOnly, bool NewIsRare)
{
	ItemName = NewItemName;
	bIsStealOnly = NewIsStealOnly;
	bIsRare = NewIsRare;
}

void AItemDrop::AutoDestroy()
{
	Destroy();
}

void AItemDrop::PickupItem(class AHectorCharacter* Player)
{
	if (!Player) return;

	if (UNobleArchimedesItemSystem* ItemSystem = Player->GetItemSystem())
	{
		ItemSystem->AddItem(ItemName, 1);
	}

	Destroy();
}

void AItemDrop::OnPlayerEnterPickup(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AHectorCharacter* Hector = Cast<AHectorCharacter>(OtherActor))
	{
		PickupItem(Hector);
	}
}
