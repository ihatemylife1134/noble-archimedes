// Copyright Epic Games, Inc. All Rights Reserved.

#include "NobleAnimGraphAuthoring.h"

#include "Animation/AnimBlueprint.h"
#include "Animation/AnimSequence.h"
#include "AnimationBlueprintLibrary.h"
#include "AnimationGraph.h"
#include "AnimationStateMachineGraph.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_Slot.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "AnimGraphNode_StateMachine.h"
#include "AnimGraphNode_StateResult.h"
#include "AnimGraphNode_TransitionResult.h"
#include "AnimStateEntryNode.h"
#include "AnimStateNode.h"
#include "AnimStateNodeBase.h"
#include "AnimStateTransitionNode.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphPin.h"
#include "EdGraph/EdGraphSchema.h"
#include "EdGraphSchema_K2.h"
#include "K2Node_VariableGet.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"

DEFINE_LOG_CATEGORY_STATIC(LogNobleAnimAuthoring, Log, All);

namespace
{
	UEdGraph* GetAnimGraph(UAnimBlueprint* AnimBlueprint)
	{
		if (!AnimBlueprint)
		{
			return nullptr;
		}

		TArray<UAnimationGraph*> Graphs;
		UAnimationBlueprintLibrary::GetAnimationGraphs(AnimBlueprint, Graphs);
		return Graphs.Num() > 0 ? Cast<UEdGraph>(Graphs[0]) : nullptr;
	}

	FString BoundGraphName(const UAnimStateNode* State)
	{
		const UEdGraph* Bound = State ? State->GetBoundGraph() : nullptr;
		return Bound ? Bound->GetName() : FString();
	}

	/** First pin pointing the requested way, optionally matching Name. */
	UEdGraphPin* FindPin(UEdGraphNode* Node, EEdGraphPinDirection Direction,
		FName Name = NAME_None)
	{
		if (!Node)
		{
			return nullptr;
		}

		for (UEdGraphPin* Pin : Node->Pins)
		{
			if (!Pin || Pin->Direction != Direction)
			{
				continue;
			}
			if (Name != NAME_None && Pin->PinName != Name)
			{
				continue;
			}
			return Pin;
		}
		return nullptr;
	}

	bool Connect(UEdGraph* Graph, UEdGraphPin* From, UEdGraphPin* To)
	{
		if (!Graph || !From || !To || From->Direction != EGPD_Output
			|| To->Direction != EGPD_Input)
		{
			return false;
		}

		const UEdGraphSchema* Schema = Graph->GetSchema();
		if (!Schema)
		{
			return false;
		}

		if (From->LinkedTo.Contains(To))
		{
			return true;
		}

		return Schema->TryCreateConnection(From, To);
	}
}

UAnimationStateMachineGraph* UNobleAnimGraphAuthoring::GetOrCreateStateMachine(
	UAnimBlueprint* AnimBlueprint, FName MachineName)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph)
	{
		UE_LOG(LogNobleAnimAuthoring, Warning, TEXT("No animation graph on %s."),
			*GetNameSafe(AnimBlueprint));
		return nullptr;
	}

	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (UAnimGraphNode_StateMachine* Existing = Cast<UAnimGraphNode_StateMachine>(Node))
		{
			if (Existing->EditorStateMachineGraph)
			{
				return Existing->EditorStateMachineGraph;
			}
		}
	}

	// Mirror FEdGraphSchemaAction_NewStateNode::PerformAction: PostPlacedNewNode
	// is what creates the EditorStateMachineGraph and its entry node.
	UAnimGraphNode_StateMachine* NewNode = NewObject<UAnimGraphNode_StateMachine>(AnimGraph);
	AnimGraph->AddNode(NewNode, true, false);
	NewNode->CreateNewGuid();
	NewNode->PostPlacedNewNode();
	NewNode->AllocateDefaultPins();
	NewNode->NodePosX = 320;
	NewNode->NodePosY = 0;

	if (!NewNode->EditorStateMachineGraph)
	{
		UE_LOG(LogNobleAnimAuthoring, Error, TEXT("State machine node created without a graph."));
		return nullptr;
	}

	FBlueprintEditorUtils::RenameGraph(NewNode->EditorStateMachineGraph, MachineName.ToString());
	UE_LOG(LogNobleAnimAuthoring, Log, TEXT("Created state machine '%s'."),
		*MachineName.ToString());
	return NewNode->EditorStateMachineGraph;
}

bool UNobleAnimGraphAuthoring::SetEntryState(UAnimationStateMachineGraph* StateMachine,
	UAnimStateNode* FirstState)
{
	if (!StateMachine || !FirstState)
	{
		return false;
	}

	return Connect(StateMachine,
		StateMachine->EntryNode ? StateMachine->EntryNode->GetOutputPin() : nullptr,
		FirstState->GetInputPin());
}

bool UNobleAnimGraphAuthoring::SetEntryStateByName(UAnimationStateMachineGraph* StateMachine,
	FName StateName)
{
	if (!StateMachine)
	{
		return false;
	}

	// Already driving a state: leave it alone.
	if (IsEntryConnected(StateMachine))
	{
		return true;
	}

	for (UEdGraphNode* Node : StateMachine->Nodes)
	{
		UAnimStateNode* State = Cast<UAnimStateNode>(Node);
		if (State && State->GetStateName() == StateName)
		{
			return SetEntryState(StateMachine, State);
		}
	}

	UE_LOG(LogNobleAnimAuthoring, Warning, TEXT("No state named '%s' to use as entry."),
		*StateName.ToString());
	return false;
}

bool UNobleAnimGraphAuthoring::IsEntryConnected(UAnimationStateMachineGraph* StateMachine)
{
	if (!StateMachine || !StateMachine->EntryNode)
	{
		return false;
	}

	UEdGraphPin* Output = StateMachine->EntryNode->GetOutputPin();
	return Output && Output->LinkedTo.Num() > 0;
}

bool UNobleAnimGraphAuthoring::EnsureStateOutputConnected(UAnimationStateMachineGraph* StateMachine,
	FName StateName)
{
	if (!StateMachine)
	{
		return false;
	}

	for (UEdGraphNode* Node : StateMachine->Nodes)
	{
		UAnimStateNode* State = Cast<UAnimStateNode>(Node);
		if (!State || State->GetStateName() != StateName)
		{
			continue;
		}

		UEdGraph* BoundGraph = State->GetBoundGraph();
		if (!BoundGraph)
		{
			return false;
		}

		UAnimGraphNode_StateResult* ResultNode = nullptr;
		UAnimGraphNode_SequencePlayer* Player = nullptr;
		for (UEdGraphNode* Inner : BoundGraph->Nodes)
		{
			if (!ResultNode)
			{
				ResultNode = Cast<UAnimGraphNode_StateResult>(Inner);
			}
			if (!Player)
			{
				Player = Cast<UAnimGraphNode_SequencePlayer>(Inner);
			}
		}

		if (!ResultNode || !Player)
		{
			UE_LOG(LogNobleAnimAuthoring, Warning,
				TEXT("State '%s' missing a result node or player."), *StateName.ToString());
			return false;
		}

		UEdGraphPin* ResultInput = FindPin(ResultNode, EGPD_Input);
		if (ResultInput && ResultInput->LinkedTo.Num() > 0)
		{
			return true;
		}

		const bool bConnected = Connect(BoundGraph,
			FindPin(Player, EGPD_Output), ResultInput);
		if (bConnected)
		{
			UE_LOG(LogNobleAnimAuthoring, Log, TEXT("State '%s' wired to its result."),
				*StateName.ToString());
		}
		return bConnected;
	}
	return false;
}

FString UNobleAnimGraphAuthoring::GetStateSequenceName(UAnimationStateMachineGraph* StateMachine,
	FName StateName)
{
	if (!StateMachine)
	{
		return FString();
	}

	for (UEdGraphNode* Node : StateMachine->Nodes)
	{
		UAnimStateNode* State = Cast<UAnimStateNode>(Node);
		if (!State || State->GetStateName() != StateName)
		{
			continue;
		}

		UEdGraph* BoundGraph = State->GetBoundGraph();
		if (!BoundGraph)
		{
			return FString();
		}

		for (UEdGraphNode* Inner : BoundGraph->Nodes)
		{
			if (UAnimGraphNode_SequencePlayer* Player = Cast<UAnimGraphNode_SequencePlayer>(Inner))
			{
				if (UAnimSequenceBase* Sequence = Player->Node.GetSequence())
				{
					return Sequence->GetName();
				}
			}
		}
	}
	return FString();
}

bool UNobleAnimGraphAuthoring::ConnectRootToStateMachine(UAnimBlueprint* AnimBlueprint,
	UAnimationStateMachineGraph* StateMachine)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph || !StateMachine)
	{
		return false;
	}

	UAnimGraphNode_Root* RootNode = nullptr;
	UAnimGraphNode_StateMachine* MachineNode = nullptr;

	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (!RootNode)
		{
			RootNode = Cast<UAnimGraphNode_Root>(Node);
		}
		if (UAnimGraphNode_StateMachine* Candidate = Cast<UAnimGraphNode_StateMachine>(Node))
		{
			if (Candidate->EditorStateMachineGraph == StateMachine)
			{
				MachineNode = Candidate;
			}
		}
	}

	if (!RootNode || !MachineNode)
	{
		UE_LOG(LogNobleAnimAuthoring, Warning,
			TEXT("Cannot connect root: root %s, state machine node %s."),
			RootNode ? TEXT("found") : TEXT("missing"),
			MachineNode ? TEXT("found") : TEXT("missing"));
		return false;
	}

	const bool bConnected = Connect(AnimGraph,
		FindPin(MachineNode, EGPD_Output),
		FindPin(RootNode, EGPD_Input));

	if (bConnected)
	{
		FBlueprintEditorUtils::MarkBlueprintAsModified(AnimBlueprint);
	}

	UE_LOG(LogNobleAnimAuthoring, Log, TEXT("Root connection %s."),
		bConnected ? TEXT("established") : TEXT("failed"));
	return bConnected;
}

bool UNobleAnimGraphAuthoring::IsRootConnected(UAnimBlueprint* AnimBlueprint)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph)
	{
		return false;
	}

	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (UAnimGraphNode_Root* RootNode = Cast<UAnimGraphNode_Root>(Node))
		{
			if (UEdGraphPin* Input = FindPin(RootNode, EGPD_Input))
			{
				return Input->LinkedTo.Num() > 0;
			}
		}
	}
	return false;
}

TArray<FName> UNobleAnimGraphAuthoring::GetStateNames(UAnimationStateMachineGraph* StateMachine)
{
	TArray<FName> Names;
	if (!StateMachine)
	{
		return Names;
	}

	for (UEdGraphNode* Node : StateMachine->Nodes)
	{
		if (const UAnimStateNode* State = Cast<UAnimStateNode>(Node))
		{
			Names.Add(FName(*BoundGraphName(State)));
		}
	}
	return Names;
}

int32 UNobleAnimGraphAuthoring::GetTransitionCount(UAnimationStateMachineGraph* StateMachine)
{
	int32 Count = 0;
	if (!StateMachine)
	{
		return Count;
	}

	for (UEdGraphNode* Node : StateMachine->Nodes)
	{
		if (Cast<UAnimStateTransitionNode>(Node))
		{
			++Count;
		}
	}
	return Count;
}

bool UNobleAnimGraphAuthoring::ConnectStateMachineToSlot(UAnimBlueprint* AnimBlueprint,
	UAnimationStateMachineGraph* StateMachine)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph || !StateMachine)
	{
		return false;
	}

	UAnimGraphNode_Slot* SlotNode = nullptr;
	UAnimGraphNode_StateMachine* MachineNode = nullptr;
	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (!SlotNode)
		{
			SlotNode = Cast<UAnimGraphNode_Slot>(Node);
		}
		if (UAnimGraphNode_StateMachine* Candidate = Cast<UAnimGraphNode_StateMachine>(Node))
		{
			if (!MachineNode || Candidate->EditorStateMachineGraph == StateMachine)
			{
				MachineNode = Candidate;
			}
		}
	}

	if (!SlotNode || !MachineNode)
	{
		UE_LOG(LogNobleAnimAuthoring, Warning,
			TEXT("Cannot feed slot: slot %s, state machine %s."),
			SlotNode ? TEXT("found") : TEXT("missing"),
			MachineNode ? TEXT("found") : TEXT("missing"));
		return false;
	}

	const bool bConnected = Connect(AnimGraph,
		FindPin(MachineNode, EGPD_Output),
		FindPin(SlotNode, EGPD_Input));

	if (bConnected)
	{
		FBlueprintEditorUtils::MarkBlueprintAsModified(AnimBlueprint);
	}

	UE_LOG(LogNobleAnimAuthoring, Log, TEXT("State machine -> slot: %s."),
		bConnected ? TEXT("connected") : TEXT("failed"));
	return bConnected;
}

bool UNobleAnimGraphAuthoring::IsStateMachineConnected(UAnimBlueprint* AnimBlueprint)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph)
	{
		return false;
	}

	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (UAnimGraphNode_StateMachine* MachineNode = Cast<UAnimGraphNode_StateMachine>(Node))
		{
			UEdGraphPin* Output = FindPin(MachineNode, EGPD_Output);
			return Output && Output->LinkedTo.Num() > 0;
		}
	}
	return false;
}

UAnimGraphNode_Slot* UNobleAnimGraphAuthoring::EnsureSlotNode(UAnimBlueprint* AnimBlueprint,
	FName SlotName)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph)
	{
		return nullptr;
	}

	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (UAnimGraphNode_Slot* Existing = Cast<UAnimGraphNode_Slot>(Node))
		{
			return Existing;
		}
	}

	// Same construction sequence the editor's own "Add Slot" action performs.
	UAnimGraphNode_Slot* NewNode = NewObject<UAnimGraphNode_Slot>(AnimGraph);
	AnimGraph->AddNode(NewNode, true, false);
	NewNode->CreateNewGuid();
	NewNode->PostPlacedNewNode();
	NewNode->Node.SlotName = SlotName;
	NewNode->AllocateDefaultPins();
	NewNode->NodePosX = 160;
	NewNode->NodePosY = 0;

	FBlueprintEditorUtils::MarkBlueprintAsModified(AnimBlueprint);
	UE_LOG(LogNobleAnimAuthoring, Log, TEXT("Created slot node '%s'."),
		*SlotName.ToString());
	return NewNode;
}

FName UNobleAnimGraphAuthoring::GetSlotName(UAnimBlueprint* AnimBlueprint)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph)
	{
		return NAME_None;
	}

	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (UAnimGraphNode_Slot* Slot = Cast<UAnimGraphNode_Slot>(Node))
		{
			return Slot->Node.SlotName;
		}
	}
	return NAME_None;
}

bool UNobleAnimGraphAuthoring::EnsureSlotPipeline(UAnimBlueprint* AnimBlueprint,
	UAnimationStateMachineGraph* StateMachine, FName SlotName)
{
	UEdGraph* AnimGraph = GetAnimGraph(AnimBlueprint);
	if (!AnimGraph || !StateMachine)
	{
		return false;
	}

	UAnimGraphNode_Slot* SlotNode = EnsureSlotNode(AnimBlueprint, SlotName);
	if (!SlotNode)
	{
		return false;
	}

	// machine -> slot, then slot -> root. The root input is re-targeted at the
	// slot because montages override the slot, not the root.
	const bool bToSlot = ConnectStateMachineToSlot(AnimBlueprint, StateMachine);

	UAnimGraphNode_Root* RootNode = nullptr;
	for (UEdGraphNode* Node : AnimGraph->Nodes)
	{
		if (UAnimGraphNode_Root* Candidate = Cast<UAnimGraphNode_Root>(Node))
		{
			RootNode = Candidate;
			break;
		}
	}
	if (!RootNode)
	{
		UE_LOG(LogNobleAnimAuthoring, Warning, TEXT("No root node in the anim graph."));
		return false;
	}

	const bool bToRoot = Connect(AnimGraph,
		FindPin(SlotNode, EGPD_Output),
		FindPin(RootNode, EGPD_Input));

	if (bToRoot)
	{
		FBlueprintEditorUtils::MarkBlueprintAsModified(AnimBlueprint);
	}

	UE_LOG(LogNobleAnimAuthoring, Log,
		TEXT("Slot pipeline '%s': machine->slot %s, slot->root %s."),
		*SlotName.ToString(),
		bToSlot ? TEXT("ok") : TEXT("failed"),
		bToRoot ? TEXT("ok") : TEXT("failed"));
	return bToRoot;
}

void UNobleAnimGraphAuthoring::DumpAnimGraph(UAnimBlueprint* AnimBlueprint)
{
	if (!AnimBlueprint)
	{
		return;
	}

	TArray<UAnimationGraph*> Graphs;
	UAnimationBlueprintLibrary::GetAnimationGraphs(AnimBlueprint, Graphs);
	UE_LOG(LogNobleAnimAuthoring, Log, TEXT("DumpAnimGraph: %d animation graph(s)."), Graphs.Num());

	for (UAnimationGraph* Graph : Graphs)
	{
		if (!Graph)
		{
			continue;
		}
		UE_LOG(LogNobleAnimAuthoring, Log, TEXT("Graph '%s' nodes=%d"),
			*Graph->GetName(), Graph->Nodes.Num());

		for (UEdGraphNode* Node : Graph->Nodes)
		{
			if (!Node)
			{
				continue;
			}

			FString Links;
			for (UEdGraphPin* Pin : Node->Pins)
			{
				if (!Pin || Pin->Direction != EGPD_Input || Pin->LinkedTo.Num() == 0)
				{
					continue;
				}
				for (UEdGraphPin* Source : Pin->LinkedTo)
				{
					Links += FString::Printf(TEXT(" [%s<-%s]"),
						*Pin->PinName.ToString(),
						Source && Source->GetOwningNode()
							? *Source->GetOwningNode()->GetClass()->GetName()
							: TEXT("null"));
				}
			}

			UE_LOG(LogNobleAnimAuthoring, Log, TEXT("  node %s%s"),
				*Node->GetClass()->GetName(), *Links);
		}
	}
}

UAnimStateNode* UNobleAnimGraphAuthoring::AddState(UAnimationStateMachineGraph* StateMachine,
	FName StateName, UAnimSequence* Sequence, bool bLoop)
{
	if (!StateMachine || StateName.IsNone())
	{
		return nullptr;
	}

	const FString DesiredName = StateName.ToString();

	for (UEdGraphNode* Node : StateMachine->Nodes)
	{
		if (UAnimStateNode* Existing = Cast<UAnimStateNode>(Node))
		{
			if (BoundGraphName(Existing) == DesiredName)
			{
				return Existing;
			}
		}
	}

	// Same sequence as FEdGraphSchemaAction_NewStateNode::PerformAction: the
	// bound graph and its State Result only exist after PostPlacedNewNode.
	UAnimStateNode* State = NewObject<UAnimStateNode>(StateMachine);
	StateMachine->AddNode(State, true, false);
	State->CreateNewGuid();
	State->PostPlacedNewNode();
	State->AllocateDefaultPins();
	State->NodePosX = 0;
	State->NodePosY = StateMachine->Nodes.Num() * 140;

	if (!State->BoundGraph)
	{
		UE_LOG(LogNobleAnimAuthoring, Error, TEXT("State '%s' has no bound graph."), *DesiredName);
		return nullptr;
	}

	FBlueprintEditorUtils::RenameGraph(State->BoundGraph, DesiredName);

	if (Sequence)
	{
		UAnimGraphNode_SequencePlayer* Player =
			NewObject<UAnimGraphNode_SequencePlayer>(State->BoundGraph);
		State->BoundGraph->AddNode(Player, true, false);
		Player->CreateNewGuid();
		Player->PostPlacedNewNode();
		Player->AllocateDefaultPins();
		Player->NodePosX = -280;
		Player->NodePosY = 0;

		Player->Node.SetSequence(Sequence);
		Player->Node.SetLoopAnimation(bLoop);

		UAnimGraphNode_StateResult* Result = State->GetResultNodeInsideState();
		if (!Connect(State->BoundGraph, FindPin(Player, EGPD_Output),
			Result ? FindPin(Result, EGPD_Input) : nullptr))
		{
			UE_LOG(LogNobleAnimAuthoring, Warning,
				TEXT("Could not wire the sequence player inside state '%s'."), *DesiredName);
		}
	}

	UE_LOG(LogNobleAnimAuthoring, Log, TEXT("Added state '%s'."), *DesiredName);
	return State;
}

UAnimStateTransitionNode* UNobleAnimGraphAuthoring::AddTransition(
	UAnimationStateMachineGraph* StateMachine, UAnimStateNode* FromState,
	UAnimStateNode* ToState, float CrossfadeSeconds, bool bAutomaticRule)
{
	if (!StateMachine || !FromState || !ToState)
	{
		return nullptr;
	}

	UAnimStateTransitionNode* Transition = nullptr;
	for (UEdGraphNode* Node : StateMachine->Nodes)
	{
		UAnimStateTransitionNode* Existing = Cast<UAnimStateTransitionNode>(Node);
		if (Existing && Existing->GetPreviousState() == FromState
			&& Existing->GetNextState() == ToState)
		{
			Transition = Existing;
			break;
		}
	}

	if (!Transition)
	{
		Transition = NewObject<UAnimStateTransitionNode>(StateMachine);
		StateMachine->AddNode(Transition, true, false);
		Transition->CreateNewGuid();
		Transition->PostPlacedNewNode();
		Transition->AllocateDefaultPins();
		Transition->CreateConnections(FromState, ToState);
	}

	Transition->CrossfadeDuration = FMath::Max(0.0f, CrossfadeSeconds);
	Transition->bAutomaticRuleBasedOnSequencePlayerInState = bAutomaticRule;
	if (bAutomaticRule)
	{
		// Negative means the crossfade finishes exactly as the player ends,
		// which is what the spec's short attack blends describe.
		Transition->AutomaticRuleTriggerTime = -1.0f;
	}

	return Transition;
}

bool UNobleAnimGraphAuthoring::AddBoolVariable(UAnimBlueprint* AnimBlueprint,
	FName VariableName, bool bDefaultValue)
{
	if (!AnimBlueprint || VariableName.IsNone())
	{
		return false;
	}

	// The authored default is only a pre-first-update value; the event graph
	// drives the variable at runtime.
	(void)bDefaultValue;

	for (const FBPVariableDescription& Variable : AnimBlueprint->NewVariables)
	{
		if (Variable.VarName == VariableName)
		{
			return true;
		}
	}

	FEdGraphPinType PinType;
	PinType.PinCategory = UEdGraphSchema_K2::PC_Boolean;

	if (!FBlueprintEditorUtils::AddMemberVariable(AnimBlueprint, VariableName, PinType))
	{
		UE_LOG(LogNobleAnimAuthoring, Warning, TEXT("Could not add bool variable '%s'."),
			*VariableName.ToString());
		return false;
	}

	return true;
}

bool UNobleAnimGraphAuthoring::SetTransitionRuleVariable(
	UAnimStateTransitionNode* Transition, FName VariableName)
{
	if (!Transition || VariableName.IsNone())
	{
		return false;
	}

	UEdGraph* RuleGraph = Transition->GetBoundGraph();
	if (!RuleGraph)
	{
		return false;
	}

	UAnimGraphNode_TransitionResult* Result = nullptr;
	for (UEdGraphNode* Node : RuleGraph->Nodes)
	{
		if (UAnimGraphNode_TransitionResult* Candidate =
			Cast<UAnimGraphNode_TransitionResult>(Node))
		{
			Result = Candidate;
			break;
		}
	}

	if (!Result)
	{
		UE_LOG(LogNobleAnimAuthoring, Warning, TEXT("Transition rule graph has no result node."));
		return false;
	}

	UK2Node_VariableGet* Getter = nullptr;
	for (UEdGraphNode* Node : RuleGraph->Nodes)
	{
		UK2Node_VariableGet* Candidate = Cast<UK2Node_VariableGet>(Node);
		if (Candidate && Candidate->VariableReference.GetMemberName() == VariableName)
		{
			Getter = Candidate;
			break;
		}
	}

	if (!Getter)
	{
		Getter = NewObject<UK2Node_VariableGet>(RuleGraph);
		Getter->VariableReference.SetSelfMember(VariableName);
		RuleGraph->AddNode(Getter, true, false);
		Getter->CreateNewGuid();
		Getter->AllocateDefaultPins();
		Getter->NodePosX = -260;
	}

	if (!Connect(RuleGraph, FindPin(Getter, EGPD_Output, VariableName),
		FindPin(Result, EGPD_Input)))
	{
		UE_LOG(LogNobleAnimAuthoring, Warning,
			TEXT("Could not wire '%s' into its transition rule."), *VariableName.ToString());
		return false;
	}

	Transition->bAutomaticRuleBasedOnSequencePlayerInState = false;
	return true;
}

bool UNobleAnimGraphAuthoring::CompileAnimBlueprint(UAnimBlueprint* AnimBlueprint)
{
	if (!AnimBlueprint)
	{
		return false;
	}

	FKismetEditorUtilities::CompileBlueprint(AnimBlueprint);
	const bool bOk = AnimBlueprint->GeneratedClass != nullptr;
	if (!bOk)
	{
		UE_LOG(LogNobleAnimAuthoring, Error, TEXT("%s failed to compile."),
			*GetNameSafe(AnimBlueprint));
	}
	return bOk;
}
