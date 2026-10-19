// Fill out your copyright notice in the Description page of Project Settings.

#include "NobleArchimedesItemSystem.h"
#include "HectorCharacter.h"

UNobleArchimedesItemSystem::UNobleArchimedesItemSystem()
{
}

bool UNobleArchimedesItemSystem::UseItem(FName ItemName, AActor* Target)
{
	if (!ItemQuantities.Contains(ItemName) || ItemQuantities[ItemName] <= 0)
	{
		return false;
	}

	if (ItemName == "Potion")
	{
		// Heal 50 HP
		if (AHectorCharacter* Char = Cast<AHectorCharacter>(Target))
		{
			float NewHealth = FMath::Min(Char->GetHealth() + 50.0f, Char->GetMaxHealth());
			Char->SetHealth(NewHealth);
		}
		ItemQuantities[ItemName]--;
		return true;
	}
	else if (ItemName == "High Potion")
	{
		// Heal 150 HP
		if (AHectorCharacter* Char = Cast<AHectorCharacter>(Target))
		{
			float NewHealth = FMath::Min(Char->GetHealth() + 150.0f, Char->GetMaxHealth());
			Char->SetHealth(NewHealth);
		}
		ItemQuantities[ItemName]--;
		return true;
	}
	else if (ItemName == "Serum")
	{
		// Cure poison/curse
		ItemQuantities[ItemName]--;
		return true;
	}
	else if (ItemName == "Uncurse")
	{
		// Remove curse
		ItemQuantities[ItemName]--;
		return true;
	}
	else if (ItemName == "Death Doll")
	{
		// Death Doll is equipped, not consumed on use
		if (AHectorCharacter* Char = Cast<AHectorCharacter>(Target))
		{
			Char->SetDeathDoll(true);
		}
		ItemQuantities[ItemName]--;
		return true;
	}

	return false;
}

int32 UNobleArchimedesItemSystem::GetItemQuantity(FName ItemName) const
{
	return ItemQuantities.Contains(ItemName) ? ItemQuantities[ItemName] : 0;
}

void UNobleArchimedesItemSystem::AddItem(FName ItemName, int32 Quantity)
{
	if (!ItemQuantities.Contains(ItemName))
	{
		ItemQuantities.Add(ItemName, 0);
	}
	ItemQuantities[ItemName] += Quantity;
}

void UNobleArchimedesItemSystem::RemoveItem(FName ItemName, int32 Quantity)
{
	if (ItemQuantities.Contains(ItemName))
	{
		ItemQuantities[ItemName] = FMath::Max(0, ItemQuantities[ItemName] - Quantity);
	}
}

bool UNobleArchimedesItemSystem::TrySteal(AActor* Target, FName& OutStolenItem)
{
	if (!CanSteal(Target)) return false;

	// Random steal chance based on enemy
	float StealChance = 0.3f; // 30% base chance
	if (FMath::FRand() < StealChance)
	{
		OutStolenItem = "Iron Shard"; // Default stolen item
		return true;
	}

	return false;
}

bool UNobleArchimedesItemSystem::CanSteal(AActor* Target) const
{
	return StealLockState.Contains(Target) && StealLockState[Target];
}