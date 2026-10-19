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

bool UNobleArchimedesItemSystem::HasDeathDoll() const
{
	return ItemQuantities.Contains("Death Doll") && ItemQuantities["Death Doll"] > 0;
}

void UNobleArchimedesItemSystem::SetDeathDoll(bool bHas)
{
	if (bHas)
	{
		AddItem("Death Doll", 1);
	}
	else
	{
		RemoveItem("Death Doll", 1);
	}
}

bool UNobleArchimedesItemSystem::TrySteal(AActor* Target, FName& OutStolenItem)
{
	if (!CanSteal(Target)) return false;

	FStealLockInfo& LockInfo = StealLockState[Target];

	// ------------------------------------------------------------------
	// Data table lookup (ItemDropTable.csv)
	// ------------------------------------------------------------------
	// At runtime we don't have a data table loaded, so this is where a
	// UDataTable lookup would go: find rows matching the target's enemy name,
	// prefer entries where IsStealOnly == true, and use their DropChance as the
	// success probability. Until then we fall back to the registered StealItem
	// (from SetStealable) with a base 30% steal chance.
	float StealChance = 0.30f; // 30% base steal chance

	FName StolenItem = LockInfo.StealItem;

	if (FMath::FRand() < StealChance)
	{
		if (!StolenItem.IsNone())
		{
			// Use the enemy-specific steal item registered via SetStealable
			// (or resolved from ItemDropTable.csv).
			OutStolenItem = StolenItem;
		}
		else
		{
			// Fallback: random item from a small steal pool.
			static const FName StealPool[] = { "Iron Shard", "Silver Ingot", "Potion", "High Potion" };
			OutStolenItem = StealPool[FMath::RandRange(0, 3)];
		}

		// Mark this target as already stolen from so it can't be stolen again.
		LockInfo.bStolenFrom = true;
		return true;
	}

	return false;
}

bool UNobleArchimedesItemSystem::CanSteal(AActor* Target) const
{
	// Stealable only while in StealLockState with bStealable == true AND the
	// enemy hasn't already been stolen from.
	if (const FStealLockInfo* Info = StealLockState.Find(Target))
	{
		return Info->bStealable && !Info->bStolenFrom;
	}
	return false;
}

void UNobleArchimedesItemSystem::SetStealable(AActor* Target, bool bStealable, FName StealItem)
{
	if (!Target) return;

	FStealLockInfo& Info = StealLockState.FindOrAdd(Target);
	Info.bStealable = bStealable;
	Info.StealItem = StealItem;

	// Opening a new steal window resets the stolen-from flag so the enemy can
	// be stolen from again (e.g. a fresh encounter/respawn).
	if (bStealable)
	{
		Info.bStolenFrom = false;
	}
}