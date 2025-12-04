from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import math
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
import os


class Answer(BaseModel):
    question_id: str
    option_value: int  # numeric representation of chosen option (0,1,2,...)


class ParticipantSubmission(BaseModel):
    participant_id: str
    answers: List[Answer]
    participant_name: Optional[str] = None  # Optional name for display


app = FastAPI(title="Mental Well-being Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory store for demo purposes
participants: Dict[str, Dict[str, Any]] = {}
profile_snapshots: List[Dict[str, Any]] = []  # Store all profile snapshots with timestamps


def build_answer_vector(answers: List[Answer]) -> Dict[str, int]:
    """
    Represent a participant's answers as a dict of question_id -> option_value.
    All participants are assumed to answer the same set of questions on the frontend.
    """
    return {a.question_id: a.option_value for a in answers}


def build_ai_feature_vector(answer_vector: Dict[str, int]) -> np.ndarray:
    """
    Convert answer vector into an AI feature vector for semantic similarity.
    This creates a multi-dimensional representation that captures:
    - Raw answer values
    - Thematic patterns (emotional, boundaries, growth, relationships)
    - Response intensity patterns
    - Overall response distribution
    """
    # Standard question order for consistent vectorization
    question_order = [
        "ack_1", "ack_2", "ack_3",
        "bp_1", "bp_2", "bp_3",
        "gd_1", "gd_2", "gd_3",
        "rc_1", "rc_2", "rc_3"
    ]
    
    # Base features: raw answer values
    base_features = [answer_vector.get(qid, 0) for qid in question_order]
    
    # Thematic features: aggregate by category
    ack_values = [answer_vector.get(f"ack_{i}", 0) for i in [1, 2, 3]]
    bp_values = [answer_vector.get(f"bp_{i}", 0) for i in [1, 2, 3]]
    gd_values = [answer_vector.get(f"gd_{i}", 0) for i in [1, 2, 3]]
    rc_values = [answer_vector.get(f"rc_{i}", 0) for i in [1, 2, 3]]
    
    # Helper function to safely compute std (returns 0 if all values are same)
    def safe_std(values):
        if len(values) <= 1:
            return 0.0
        std_val = np.std(values)
        return std_val if not np.isnan(std_val) else 0.0
    
    thematic_features = [
        np.mean(ack_values) if ack_values else 0.0, safe_std(ack_values),  # Acknowledgement stats
        np.mean(bp_values) if bp_values else 0.0, safe_std(bp_values),    # Boundaries stats
        np.mean(gd_values) if gd_values else 0.0, safe_std(gd_values),    # Growth stats
        np.mean(rc_values) if rc_values else 0.0, safe_std(rc_values),    # Relationships stats
    ]
    
    # Pattern features: response intensity and distribution
    all_values = list(answer_vector.values())
    pattern_features = [
        np.mean(all_values) if all_values else 0.0,           # Average response intensity
        safe_std(all_values),                                  # Response variability
        np.max(all_values) if all_values else 0.0,            # Peak intensity
        np.min(all_values) if all_values else 0.0,            # Minimum intensity
        len([v for v in all_values if v >= 2]) / len(all_values) if all_values else 0,  # High-intensity ratio
        len([v for v in all_values if v <= 1]) / len(all_values) if all_values else 0,  # Low-intensity ratio
    ]
    
    # Combine all features into a single vector
    feature_vector = np.array(base_features + thematic_features + pattern_features, dtype=np.float64)
    
    # Normalize to prevent scale bias
    # Use a small epsilon to avoid division by zero
    norm = np.linalg.norm(feature_vector)
    if norm > 1e-10:  # Use epsilon instead of 0 to handle floating point precision
        feature_vector = feature_vector / norm
    else:
        # If norm is zero (all answers are 0), return zero vector
        feature_vector = np.zeros_like(feature_vector)
    
    return feature_vector


def compute_similarity(vec_a: Dict[str, int], vec_b: Dict[str, int]) -> float:
    """
    AI-based similarity using cosine similarity on multi-dimensional feature vectors.
    This captures semantic patterns beyond exact matches, including:
    - Thematic alignment (emotional patterns, boundaries, growth, relationships)
    - Response intensity patterns
    - Overall mental health profile similarity
    
    Returns a score between 0 and 1, where 1.0 = identical patterns.
    """
    if not vec_a or not vec_b:
        return 0.0

    # First check exact match ratio - if 100% identical, return 1.0 immediately
    shared_questions = set(vec_a.keys()) & set(vec_b.keys())
    if shared_questions:
        exact_matches = sum(1 for q in shared_questions if vec_a[q] == vec_b[q])
        exact_ratio = exact_matches / len(shared_questions)
        
        # If all answers are identical, return 1.0 (perfect match)
        if exact_ratio >= 1.0:
            return 1.0
    else:
        exact_ratio = 0.0

    # Build AI feature vectors for semantic similarity
    try:
        features_a = build_ai_feature_vector(vec_a)
        features_b = build_ai_feature_vector(vec_b)
        
        # Check for NaN or invalid values
        if np.any(np.isnan(features_a)) or np.any(np.isnan(features_b)):
            # Fall back to exact match ratio if feature vectors are invalid
            return exact_ratio
        
        # Compute cosine similarity (AI-based semantic similarity)
        similarity_matrix = cosine_similarity(
            features_a.reshape(1, -1),
            features_b.reshape(1, -1)
        )
        ai_similarity = float(similarity_matrix[0][0])
        
        # Handle NaN or invalid cosine similarity
        if np.isnan(ai_similarity) or ai_similarity < 0:
            ai_similarity = exact_ratio
        
    except Exception as e:
        # If AI computation fails, fall back to exact matching
        print(f"Warning: AI similarity computation failed, using exact match: {e}")
        return exact_ratio
    
    # Combine AI similarity with exact matches
    # For high exact matches, weight exact ratio more heavily
    if exact_ratio >= 0.9:
        # If exact match is already high, trust it more
        combined_similarity = (exact_ratio * 0.6) + (ai_similarity * 0.4)
    else:
        # Otherwise, use balanced weighting
        combined_similarity = (ai_similarity * 0.6) + (exact_ratio * 0.4)
    
    # Ensure result is between 0 and 1
    final_similarity = max(0.0, min(1.0, combined_similarity))
    
    return final_similarity


def generate_profile(answer_vector: Dict[str, int]) -> Dict[str, Any]:
    """
    Very simple rule-based profile generator.
    Maps responses to scores across a few dimensions and returns a summary.
    This can be made more sophisticated later.
    """
    # Initialize dimensions
    dimensions = {
        "emotional_clarity": 0,
        "stress_management": 0,
        "growth_mindset": 0,
        "boundaries": 0,
        "relationship_safety": 0,
    }

    # Example: tie some question IDs to certain dimensions.
    # These IDs must match the frontend question_ids.
    for qid, value in answer_vector.items():
        # Acknowledgement
        if qid in {"ack_1", "ack_2", "ack_3"}:
            dimensions["emotional_clarity"] += value
        # Boundaries & Priorities
        if qid in {"bp_1", "bp_2", "bp_3"}:
            dimensions["boundaries"] += value
            dimensions["stress_management"] += value
        # Growth & Direction
        if qid in {"gd_1", "gd_2", "gd_3"}:
            dimensions["growth_mindset"] += value
        # Relationships & Communication
        if qid in {"rc_1", "rc_2", "rc_3"}:
            dimensions["relationship_safety"] += value

    # Normalise scores into 0–1 range assuming options 0–3 and up to 3 questions per theme
    max_per_question = 3
    max_questions_per_dim = 3
    max_score = max_per_question * max_questions_per_dim

    normalized = {k: (v / max_score) if max_score else 0.0 for k, v in dimensions.items()}

    summary_parts = []
    if normalized["emotional_clarity"] >= 0.7:
        summary_parts.append("You show strong emotional awareness and reflection.")
    elif normalized["emotional_clarity"] <= 0.3:
        summary_parts.append("You may be in a phase where your inner world feels unclear or heavy.")

    if normalized["stress_management"] >= 0.7:
        summary_parts.append("You tend to recognize patterns in your stress and have some strategies to cope.")
    elif normalized["stress_management"] <= 0.3:
        summary_parts.append("Stress may be building up in ways that are hard to manage sustainably.")

    if normalized["growth_mindset"] >= 0.7:
        summary_parts.append("You seem to be growing a lot through self-reflection and change.")
    elif normalized["growth_mindset"] <= 0.3:
        summary_parts.append("You might be feeling a bit stuck or unsure about your direction right now.")

    if normalized["boundaries"] >= 0.7:
        summary_parts.append("You are actively thinking about protecting your time, energy, and peace.")
    elif normalized["boundaries"] <= 0.3:
        summary_parts.append("There may be opportunities to set gentler boundaries for yourself.")

    if normalized["relationship_safety"] >= 0.7:
        summary_parts.append("Safe and supportive connections seem important and present in your life.")
    elif normalized["relationship_safety"] <= 0.3:
        summary_parts.append("You may be craving deeper understanding and safety in relationships.")

    if not summary_parts:
        summary_parts.append(
            "Your responses suggest a mix of strengths and growth areas across emotions, boundaries, stress, and relationships."
        )

    return {
        "dimensions": normalized,
        "summary": " ".join(summary_parts),
    }


@app.post("/api/submit")
def submit_responses(payload: ParticipantSubmission):
    """
    Store participant responses, generate individual profile snapshot,
    and return the profile along with any highly similar participants (>= 0.9).
    Uses AI-based evaluation for similarity detection.
    """
    answer_vector = build_answer_vector(payload.answers)
    profile = generate_profile(answer_vector)
    
    # Create profile snapshot with timestamp
    snapshot = {
        "participant_id": payload.participant_id,
        "participant_name": payload.participant_name or payload.participant_id,
        "answers": answer_vector,
        "profile": profile,
        "timestamp": datetime.now().isoformat(),
        "ai_feature_vector": build_ai_feature_vector(answer_vector).tolist(),
    }
    
    # Store in participants dict (for quick lookup)
    participants[payload.participant_id] = {
        "id": payload.participant_id,
        "name": payload.participant_name or payload.participant_id,
        "answers": answer_vector,
        "profile": profile,
        "timestamp": snapshot["timestamp"],
    }
    
    # Store snapshot in history
    profile_snapshots.append(snapshot)

    # AI-based similarity computation with existing participants
    similarities = []
    for other_id, other_data in participants.items():
        if other_id == payload.participant_id:
            continue
        score = compute_similarity(answer_vector, other_data["answers"])
        
        # Debug logging (can be removed in production)
        print(f"Comparing {payload.participant_id} with {other_id}: similarity = {score:.4f} ({score*100:.2f}%)")
        
        if score >= 0.9:
            similarities.append(
                {
                    "participant_id": other_id,
                    "participant_name": other_data.get("name", other_id),
                    "similarity": round(score, 4),
                    "similarity_percentage": round(score * 100, 2),
                }
            )
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "participant_id": payload.participant_id,
        "participant_name": payload.participant_name or payload.participant_id,
        "profile": profile,
        "profile_snapshot": snapshot,
        "highly_similar_participants": similarities,
        "has_similar_matches": len(similarities) > 0,
        "submission_timestamp": snapshot["timestamp"],
    }


@app.get("/api/participants")
def list_participants():
    """
    Return all stored participants, their profiles, and similarity pairs >= 0.9.
    Useful for an overview after many submissions (e.g., 200–250 participants).
    """
    ids = list(participants.keys())
    similarity_pairs = []

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a = participants[ids[i]]
            b = participants[ids[j]]
            score = compute_similarity(a["answers"], b["answers"])
            if score >= 0.9:
                similarity_pairs.append(
                    {
                        "participant_a": a["id"],
                        "participant_a_name": a.get("name", a["id"]),
                        "participant_b": b["id"],
                        "participant_b_name": b.get("name", b["id"]),
                        "similarity": round(score, 4),
                        "similarity_percentage": round(score * 100, 2),
                    }
                )

    return {
        "count": len(participants),
        "participants": participants,
        "profile_snapshots_count": len(profile_snapshots),
        "highly_similar_pairs": similarity_pairs,
    }


@app.get("/api/snapshots")
def get_snapshots():
    """Return all profile snapshots stored for future comparison."""
    return {
        "count": len(profile_snapshots),
        "snapshots": profile_snapshots,
    }


@app.get("/api/debug/similarity/{id1}/{id2}")
def debug_similarity(id1: str, id2: str):
    """Debug endpoint to check similarity between two participants."""
    if id1 not in participants or id2 not in participants:
        return {"error": "One or both participants not found"}
    
    p1 = participants[id1]
    p2 = participants[id2]
    
    score = compute_similarity(p1["answers"], p2["answers"])
    
    # Also compute exact match details
    shared_questions = set(p1["answers"].keys()) & set(p2["answers"].keys())
    exact_matches = sum(1 for q in shared_questions if p1["answers"][q] == p2["answers"][q])
    exact_ratio = exact_matches / len(shared_questions) if shared_questions else 0.0
    
    return {
        "participant_1": id1,
        "participant_2": id2,
        "similarity_score": round(score, 4),
        "similarity_percentage": round(score * 100, 2),
        "exact_match_ratio": round(exact_ratio, 4),
        "exact_match_percentage": round(exact_ratio * 100, 2),
        "meets_threshold": score >= 0.9,
        "total_questions": len(shared_questions),
        "matching_questions": exact_matches,
    }


@app.delete("/api/reset")
def reset():
    """Clear all stored participants and snapshots (for testing/demo)."""
    participants.clear()
    profile_snapshots.clear()
    return {"status": "ok", "message": "All participants and snapshots cleared."}


# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def read_root():
    """Serve the frontend index.html"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found. Please ensure static/index.html exists."}


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (for production deployments) or default to 8000
    port = int(os.getenv("PORT", 8000))
    # Disable reload in production (set RELOAD env var to enable)
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"🚀 Starting Mental Well-being Agent server...")
    print(f"📡 Server will be available at: http://0.0.0.0:{port}")
    print(f"🌐 Access from other devices: http://{get_local_ip()}:{port}")
    print(f"📱 Generate QR code: python generate_qr.py http://{get_local_ip()}:{port}")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=reload)


def get_local_ip():
    """Get the local IP address for QR code generation."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


