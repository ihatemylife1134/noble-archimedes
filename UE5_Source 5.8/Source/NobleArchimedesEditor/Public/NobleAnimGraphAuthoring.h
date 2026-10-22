// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NobleAnimGraphAuthoring.generated.h"

class UAnimBlueprint;
class UAnimSequence;
class UAnimStateNode;
class UAnimStateTransitionNode;
class UAnimGraphNode_Slot;
class UAnimationStateMachineGraph;

/**
 * Script-callable helpers for authoring Animation Blueprint state machines.
 *
 * UE 5.8 does not let Python add nodes to an AnimationStateMachineGraph: the
 * graph's Nodes/EntryNode arrays and UAnimStateNode::BoundGraph are plain
 * UPROPERTYs, which PropertyAccessUtil denies to script. This library performs
 * the same construction the editor's "Add State" / drag-transition actions do,
 * so the content pipeline can generate the Hector state machine.
 *
 * Every entry point is idempotent: running the build twice does not duplicate
 * states or transitions.
 */
UCLASS()
class NOBLEARCHIMEDESEDITOR_API UNobleAnimGraphAuthoring : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Returns the AnimBlueprint's animation graph, creating nothing. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static UAnimationStateMachineGraph* GetOrCreateStateMachine(UAnimBlueprint* AnimBlueprint,
		FName MachineName = FName("Locomotion"));

	/** Adds a state playing Sequence, or returns the existing state of that name. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static UAnimStateNode* AddState(UAnimationStateMachineGraph* StateMachine,
		FName StateName, UAnimSequence* Sequence, bool bLoop);

	/** Adds a transition between two states, reusing an existing one if present. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static UAnimStateTransitionNode* AddTransition(UAnimationStateMachineGraph* StateMachine,
		UAnimStateNode* FromState, UAnimStateNode* ToState, float CrossfadeSeconds,
		bool bAutomaticRule);

	/** Makes the state machine entry node point at FirstState. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool SetEntryState(UAnimationStateMachineGraph* StateMachine, UAnimStateNode* FirstState);

	/**
	 * Points the entry node at the state with this name (no-op if already set).
	 * Returns false when the state does not exist.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool SetEntryStateByName(UAnimationStateMachineGraph* StateMachine, FName StateName);

	/** True when the entry node drives a state. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool IsEntryConnected(UAnimationStateMachineGraph* StateMachine);

	/** Reports the sequence playing in a state (empty when unset). */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static FString GetStateSequenceName(UAnimationStateMachineGraph* StateMachine, FName StateName);

	/**
	 * Makes sure a state's player feeds its state-result node.
	 *
	 * A state whose bound graph has a sequence player but no link to the result
	 * outputs the reference pose, which looks exactly like a T-pose even though
	 * the machine, entry and clips are all correct.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool EnsureStateOutputConnected(UAnimationStateMachineGraph* StateMachine, FName StateName);

	/**
	 * Connects the state machine's output pose to the animation graph's Root node.
	 *
	 * Without this the machine evaluates but its pose is discarded, so the mesh
	 * holds the reference pose (the T-pose seen in playtests) no matter which
	 * state is active.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool ConnectRootToStateMachine(UAnimBlueprint* AnimBlueprint,
		UAnimationStateMachineGraph* StateMachine);

	/** True when the anim graph Root node has an incoming pose connection. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool IsRootConnected(UAnimBlueprint* AnimBlueprint);

	/** Adds a bool member variable to the AnimBlueprint (no-op if it exists). */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool AddBoolVariable(UAnimBlueprint* AnimBlueprint, FName VariableName,
		bool bDefaultValue);

	/** Uses a bool variable as a transition rule (true = take the transition). */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool SetTransitionRuleVariable(UAnimStateTransitionNode* Transition,
		FName VariableName);

	/** Compiles the AnimBlueprint and reports whether it produced a class. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool CompileAnimBlueprint(UAnimBlueprint* AnimBlueprint);

	/** Lists the state names in a state machine, for verification. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static TArray<FName> GetStateNames(UAnimationStateMachineGraph* StateMachine);

	/** Counts transitions in a state machine, for verification. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static int32 GetTransitionCount(UAnimationStateMachineGraph* StateMachine);

	/** Logs the anim graph's nodes and their input links, for diagnosis. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static void DumpAnimGraph(UAnimBlueprint* AnimBlueprint);

	/**
	 * Feeds the state machine's pose into the graph's Slot node.
	 *
	 * The generated graph wired Root <- Slot <- (empty) SequencePlayer and left the
	 * state machine dangling, so the base pose was the reference pose and only
	 * montages (which override the Slot) appeared to animate.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool ConnectStateMachineToSlot(UAnimBlueprint* AnimBlueprint,
		UAnimationStateMachineGraph* StateMachine);

	/** True when the state machine actually contributes to the final pose. */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool IsStateMachineConnected(UAnimBlueprint* AnimBlueprint);

	/**
	 * Returns the anim graph's slot node, creating it when absent.
	 *
	 * A factory-created AnimBlueprint has no slot node, so
	 * ConnectStateMachineToSlot finds nothing to feed and returns false, leaving
	 * the machine wired straight to the Root. Montages override a slot rather
	 * than the Root, so without this the base locomotion pose animates but
	 * attacks never appear.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static UAnimGraphNode_Slot* EnsureSlotNode(UAnimBlueprint* AnimBlueprint,
		FName SlotName = FName("DefaultSlot"));

	/** Reports the slot name an existing slot node uses (None when there is none). */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static FName GetSlotName(UAnimBlueprint* AnimBlueprint);

	/**
	 * Wires the full pose path: machine -> slot -> root.
	 *
	 * Use this instead of ConnectRootToStateMachine when the AnimBlueprint may
	 * not have a slot node yet.
	 */
	UFUNCTION(BlueprintCallable, Category = "Noble|Animation")
	static bool EnsureSlotPipeline(UAnimBlueprint* AnimBlueprint,
		UAnimationStateMachineGraph* StateMachine, FName SlotName);
};
