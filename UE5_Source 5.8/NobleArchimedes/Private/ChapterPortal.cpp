// Fill out your copyright notice in the Description page of Project Settings.

#include "ChapterPortal.h"
#include "EnemyBase.h"
#include "NobleArchimedesGameModeBase.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

AChapterPortal::AChapterPortal()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickInterval = 0.25f;

	Trigger = CreateDefaultSubobject<UBoxComponent>(TEXT("Trigger"));
	RootComponent = Trigger;
	Trigger->SetBoxExtent(FVector(180.0f, 180.0f, 140.0f));
	Trigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Trigger->SetCollisionResponseToAllChannels(ECollisionResponse::ECR_Ignore);
	Trigger->SetCollisionResponseToChannel(ECC_Pawn, ECollisionResponse::ECR_Overlap);

	PortalMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PortalMesh"));
	PortalMesh->SetupAttachment(Trigger);
	PortalMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	PortalMesh->SetRelativeScale3D(FVector(2.4f, 0.15f, 3.0f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeMesh.Succeeded())
	{
		PortalMesh->SetStaticMesh(CubeMesh.Object);
	}
}

void AChapterPortal::BeginPlay()
{
	Super::BeginPlay();
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &AChapterPortal::OnTriggerBeginOverlap);
}

void AChapterPortal::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (bActivating)
	{
		return;
	}

	const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	if (!Player)
	{
		return;
	}

	const float RadiusSq = FMath::Square(ActivationRadius);
	if (FVector::DistSquared2D(Player->GetActorLocation(), GetActorLocation()) <= RadiusSq
		&& CanActivate())
	{
		ActivatePortal();
	}
}

bool AChapterPortal::CanActivate() const
{
	if (!bRequireBossDefeated)
	{
		return true;
	}

	for (TActorIterator<AEnemyBase> It(GetWorld()); It; ++It)
	{
		if (It->bIsBoss && !It->bIsDead)
		{
			return false;
		}
	}
	return true;
}

void AChapterPortal::ActivatePortal()
{
	if (bActivating || !CanActivate())
	{
		return;
	}

	bActivating = true;

	if (ANobleArchimedesGameModeBase* GameMode =
		Cast<ANobleArchimedesGameModeBase>(UGameplayStatics::GetGameMode(this)))
	{
		if (bCompleteCurrentChapter)
		{
			GameMode->CompleteChapter(GameMode->GetCurrentChapter());
		}
		GameMode->StartChapter(TargetChapter);
	}

	if (TargetLevelName.IsNone())
	{
		UE_LOG(LogTemp, Warning, TEXT("NobleArchimedes: chapter portal has no target level."));
		bActivating = false;
		return;
	}

	UE_LOG(LogTemp, Log, TEXT("NobleArchimedes: chapter portal opening %s (chapter %d)."),
		*TargetLevelName.ToString(), TargetChapter);
	UGameplayStatics::OpenLevel(this, TargetLevelName);
}

void AChapterPortal::OnTriggerBeginOverlap(
	UPrimitiveComponent* OverlappedComponent,
	AActor* OtherActor,
	UPrimitiveComponent* OtherComp,
	int32 OtherBodyIndex,
	bool bFromSweep,
	const FHitResult& SweepResult)
{
	if (Cast<APawn>(OtherActor) && CanActivate())
	{
		ActivatePortal();
	}
}
