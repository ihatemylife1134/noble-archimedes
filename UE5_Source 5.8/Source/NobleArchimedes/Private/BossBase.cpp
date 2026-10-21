// Fill out your copyright notice in the Description page of Project Settings.

#include "BossBase.h"

// Sets default values
ABossBase::ABossBase()
{
	bIsBoss = true;
	BossPhase = 1;
	bHasSecondPhase = false;
	bHasThirdPhase = false;
}

void ABossBase::BeginPlay()
{
	Super::BeginPlay();

	// Boss stats are authored in EnemyDataTable.csv. Do not multiply them here,
	// or the data-driven encounter values become impossible to reason about.
	MaxHealth = FMath::Max(1.0f, MaxHealth);
	CurrentHealth = MaxHealth;

	// Boss phase count follows the authored phase flags. This keeps the
	// threshold list and the phase cap in sync instead of transitioning past
	// the configured maximum.
	if (bHasThirdPhase)
	{
		MaxBossPhases = 3;
	}
	else if (bHasSecondPhase || MaxBossPhases >= 2)
	{
		MaxBossPhases = 2;
	}
	else
	{
		MaxBossPhases = 1;
	}

	PhaseTransitionHealthThresholds.Empty();
	if (MaxBossPhases == 3)
	{
		PhaseTransitionHealthThresholds.Add(0.66f);
		PhaseTransitionHealthThresholds.Add(0.33f);
	}
	else if (MaxBossPhases == 2)
	{
		PhaseTransitionHealthThresholds.Add(0.5f);
	}
}

void ABossBase::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsDead) return;

	CheckPhaseTransition();
}

void ABossBase::TransitionToPhase(int32 NewPhase)
{
	BossPhase = NewPhase;

	// Boss phase transition effects would be handled in Blueprint
	// - Play phase transition animation
	// - Change attack patterns
	// - Update visual appearance
}

bool ABossBase::IsPhaseTransitionNeeded() const
{
	if (CurrentHealth <= 0.0f || MaxHealth <= 0.0f) return false;

	float HealthPercent = CurrentHealth / MaxHealth;

	for (float Threshold : PhaseTransitionHealthThresholds)
	{
		if (HealthPercent <= Threshold && BossPhase < MaxBossPhases)
		{
			return true;
		}
	}

	return false;
}

void ABossBase::CheckPhaseTransition()
{
	if (CurrentHealth <= 0.0f || MaxHealth <= 0.0f)
	{
		return;
	}

	const float HealthPercent = CurrentHealth / MaxHealth;

	// Thresholds are authored high-to-low. Pick the highest phase whose
	// threshold has been crossed so a large hit cannot skip a phase.
	int32 DesiredPhase = 1;
	for (int32 Index = 0; Index < PhaseTransitionHealthThresholds.Num(); ++Index)
	{
		if (HealthPercent <= PhaseTransitionHealthThresholds[Index])
		{
			DesiredPhase = FMath::Max(DesiredPhase, Index + 2);
		}
	}

	DesiredPhase = FMath::Min(DesiredPhase, MaxBossPhases);
	if (DesiredPhase > BossPhase)
	{
		TransitionToPhase(DesiredPhase);
	}
}

void ABossBase::PlayBossIntro()
{
	// Boss intro cutscene would be triggered here
}

void ABossBase::PlayBossVictory()
{
	// Boss victory animation would be played here
}
