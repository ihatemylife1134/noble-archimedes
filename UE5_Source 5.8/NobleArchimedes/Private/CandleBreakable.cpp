// Fill out your copyright notice in the Description page of Project Settings.

#include "CandleBreakable.h"
#include "HectorCharacter.h"
#include "ItemDrop.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Kismet/GameplayStatics.h"

// Sets default values
ACandleBreakable::ACandleBreakable()
{
	PrimaryActorTick.bCanEverTick = true;

	CandleMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CandleMesh"));
	RootComponent = CandleMesh;

	FlameParticle = CreateDefaultSubobject<UParticleSystemComponent>(TEXT("FlameParticle"));
	FlameParticle->SetupAttachment(CandleMesh);

	// Set up hit event
	CandleMesh->OnComponentHit.AddDynamic(this, &ACandleBreakable::OnCandleHit);
}

void ACandleBreakable::BeginPlay()
{
	Super::BeginPlay();
	bIsBroken = false;
}

void ACandleBreakable::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void ACandleBreakable::BreakCandle()
{
	if (bIsBroken) return;

	bIsBroken = true;

	// Hide candle mesh and flame
	if (CandleMesh) CandleMesh->SetVisibility(false);
	if (FlameParticle) FlameParticle->SetVisibility(false);

	// Attempt to drop an item
	if (FMath::FRand() < DropChance && PossibleDrops.Num() > 0)
	{
		int32 DropIndex = FMath::RandRange(0, PossibleDrops.Num() - 1);
		SpawnDropItem(PossibleDrops[DropIndex]);
	}

	// Disable collision
	CandleMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

bool ACandleBreakable::IsCandleBroken() const
{
	return bIsBroken;
}

void ACandleBreakable::OnCandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	FVector NormalImpulse, const FHitResult& Hit)
{
	// Break candle when attacked by player
	if (OtherActor && !bIsBroken)
	{
		if (AHectorCharacter* Hector = Cast<AHectorCharacter>(OtherActor))
		{
			BreakCandle();
		}
	}
}

void ACandleBreakable::SpawnDropItem(FName ItemName)
{
	if (!GetWorld()) return;

	FActorSpawnParameters SpawnParams;
	SpawnParams.Owner = this;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	UClass* DropClass = ItemDropClass ? ItemDropClass.Get() : AItemDrop::StaticClass();
	AItemDrop* Drop = GetWorld()->SpawnActor<AItemDrop>(
		DropClass,
		GetActorLocation() + FVector(0.0f, 0.0f, 50.0f),
		FRotator::ZeroRotator,
		SpawnParams);
	if (Drop)
	{
		Drop->InitializeItem(ItemName, false, false);
	}
}
