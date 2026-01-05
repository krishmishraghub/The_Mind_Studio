# Technical Deep-Dive: Mental Well-being Agent

## 🔬 Algorithm & Implementation Details

### 1. Feature Vector Construction

**Question: How exactly does the 26-dimensional feature vector work?**

The feature vector is constructed in three layers:

```python
# Layer 1: Base Features (12 dimensions)
base_features = [answer_vector.get(qid, 0) for qid in question_order]
# Example: [0, 1, 2, 1, 0, 3, 2, 1, 0, 1, 2, 3]

# Layer 2: Thematic Features (8 dimensions)
# For each category (ack, bp, gd, rc):
#   - Mean of answers in that category
#   - Standard deviation of answers in that category
thematic_features = [
    np.mean(ack_values), np.std(ack_values),  # Acknowledgement
    np.mean(bp_values), np.std(bp_values),    # Boundaries
    np.mean(gd_values), np.std(gd_values),    # Growth
    np.mean(rc_values), np.std(rc_values),     # Relationships
]

# Layer 3: Pattern Features (6 dimensions)
pattern_features = [
    np.mean(all_values),           # Overall average intensity
    np.std(all_values),             # Response variability
    np.max(all_values),             # Peak intensity
    np.min(all_values),             # Minimum intensity
    high_intensity_ratio,           # % of answers >= 2
    low_intensity_ratio,            # % of answers <= 1
]
```

**Why this structure?**
- **Base features**: Capture raw answer patterns
- **Thematic features**: Capture category-level patterns (e.g., someone consistently high in "Acknowledgement")
- **Pattern features**: Capture overall response style (e.g., someone who always picks extreme values vs. moderate)

**Example Calculation:**
```python
# Participant A answers:
# ack_1=2, ack_2=3, ack_3=1
# bp_1=0, bp_2=1, bp_3=2
# gd_1=3, gd_2=2, gd_3=3
# rc_1=1, rc_2=1, rc_3=0

# Base features: [2, 3, 1, 0, 1, 2, 3, 2, 3, 1, 1, 0]

# Thematic features:
# ack_mean = (2+3+1)/3 = 2.0, ack_std = 0.82
# bp_mean = (0+1+2)/3 = 1.0, bp_std = 0.82
# gd_mean = (3+2+3)/3 = 2.67, gd_std = 0.47
# rc_mean = (1+1+0)/3 = 0.67, rc_std = 0.47

# Pattern features:
# mean = 1.58, std = 1.08, max = 3, min = 0
# high_ratio = 5/12 = 0.42, low_ratio = 4/12 = 0.33
```

---

### 2. Cosine Similarity Deep Dive

**Question: Why cosine similarity and how does it work mathematically?**

**Mathematical Formula:**
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
                        = Σ(Ai × Bi) / (√ΣAi² × √ΣBi²)
```

**Why it works for this use case:**
1. **Direction over Magnitude**: Measures angle between vectors, not distance
   - Two participants with similar patterns but different intensity levels still match
   - Example: [1,2,1] vs [2,4,2] have cosine similarity = 1.0 (same pattern, different scale)

2. **Normalized Vectors**: Our feature vectors are L2-normalized, so:
   ```
   ||A|| = ||B|| = 1
   cosine_similarity(A, B) = A · B (dot product)
   ```

3. **Range**: Returns values between -1 and 1
   - 1.0 = identical direction (perfect match)
   - 0.0 = orthogonal (no relationship)
   - -1.0 = opposite direction (completely different)

**Code Implementation:**
```python
from sklearn.metrics.pairwise import cosine_similarity

# Reshape to 2D array (required by sklearn)
features_a = features_a.reshape(1, -1)  # Shape: (1, 26)
features_b = features_b.reshape(1, -1)   # Shape: (1, 26)

# Compute similarity matrix
similarity_matrix = cosine_similarity(features_a, features_b)
# Returns: [[0.95]] (2D array)
ai_similarity = float(similarity_matrix[0][0])  # Extract scalar: 0.95
```

**Time Complexity**: O(n) where n = feature vector dimension (26)
**Space Complexity**: O(1) for single comparison

---

### 3. Similarity Score Combination

**Question: How do you combine exact match ratio with cosine similarity?**

The algorithm uses adaptive weighting:

```python
if exact_ratio >= 0.9:
    # High exact match: trust exact matches more (60% weight)
    combined = (exact_ratio * 0.6) + (ai_similarity * 0.4)
else:
    # Lower exact match: trust AI similarity more (60% weight)
    combined = (ai_similarity * 0.6) + (exact_ratio * 0.4)
```

**Why adaptive weighting?**
- **High exact match (≥90%)**: If answers are already very similar, exact matches are reliable
- **Lower exact match (<90%)**: AI similarity can find semantic patterns that exact matching misses

**Example Scenarios:**

**Scenario 1: High Exact Match**
```python
exact_ratio = 0.92  # 11/12 questions match
ai_similarity = 0.88  # Feature vectors are similar
combined = (0.92 * 0.6) + (0.88 * 0.4) = 0.904
# Result: 90.4% similarity (above threshold)
```

**Scenario 2: Low Exact Match, High AI Similarity**
```python
exact_ratio = 0.50  # Only 6/12 questions match exactly
ai_similarity = 0.95  # But patterns are very similar
combined = (0.95 * 0.6) + (0.50 * 0.4) = 0.77
# Result: 77% similarity (below threshold, but captures semantic similarity)
```

**Scenario 3: Perfect Match**
```python
exact_ratio = 1.0  # All answers identical
# Early return: similarity = 1.0 (no computation needed)
```

---

### 4. Normalization Strategy

**Question: Why normalize feature vectors and how?**

**L2 Normalization (Euclidean norm):**
```python
norm = np.linalg.norm(feature_vector)  # √(Σxi²)
if norm > 1e-10:
    feature_vector = feature_vector / norm
```

**Why normalize?**
1. **Scale Independence**: Prevents features with larger values from dominating
2. **Fair Comparison**: All feature vectors have unit length (||v|| = 1)
3. **Cosine Similarity**: Required for cosine similarity to work correctly

**Example:**
```python
# Without normalization:
vector_a = [1, 2, 3, 10, 20]  # Last two features dominate
vector_b = [1, 2, 3, 1, 2]

# With normalization:
vector_a_norm = [0.04, 0.08, 0.12, 0.40, 0.80]  # All features contribute equally
vector_b_norm = [0.22, 0.44, 0.67, 0.22, 0.44]
```

**Edge Case Handling:**
```python
if norm <= 1e-10:  # All zeros or very small
    feature_vector = np.zeros_like(feature_vector)  # Return zero vector
```

---

### 5. Profile Generation Algorithm

**Question: How are the 5 dimensions calculated?**

**Dimension Mapping:**
```python
dimensions = {
    "emotional_clarity": 0,      # From ack_1, ack_2, ack_3
    "stress_management": 0,      # From bp_1, bp_2, bp_3
    "growth_mindset": 0,          # From gd_1, gd_2, gd_3
    "boundaries": 0,              # From bp_1, bp_2, bp_3
    "relationship_safety": 0,     # From rc_1, rc_2, rc_3
}

# Accumulate scores
for qid, value in answer_vector.items():
    if qid in {"ack_1", "ack_2", "ack_3"}:
        dimensions["emotional_clarity"] += value
    if qid in {"bp_1", "bp_2", "bp_3"}:
        dimensions["boundaries"] += value
        dimensions["stress_management"] += value  # Shared with boundaries
    # ... etc
```

**Normalization:**
```python
max_per_question = 3
max_questions_per_dim = 3
max_score = max_per_question * max_questions_per_dim  # 3 * 3 = 9

normalized = {k: (v / max_score) for k, v in dimensions.items()}
# Result: values between 0.0 and 1.0
```

**Example:**
```python
# Participant answers:
# ack_1=2, ack_2=3, ack_3=1
# emotional_clarity = 2 + 3 + 1 = 6
# normalized = 6 / 9 = 0.67 (67%)
```

**Summary Generation:**
```python
if normalized["emotional_clarity"] >= 0.7:
    summary_parts.append("You show strong emotional awareness...")
elif normalized["emotional_clarity"] <= 0.3:
    summary_parts.append("You may be in a phase where...")
```

---

### 6. API Endpoint Implementation

**Question: How does the `/api/submit` endpoint process requests?**

**Request Flow:**
```python
@app.post("/api/submit")
def submit_responses(payload: ParticipantSubmission):
    # 1. Build answer vector
    answer_vector = build_answer_vector(payload.answers)
    # Result: {"ack_1": 2, "ack_2": 3, ...}
    
    # 2. Generate profile
    profile = generate_profile(answer_vector)
    # Result: {"dimensions": {...}, "summary": "..."}
    
    # 3. Create snapshot
    snapshot = {
        "participant_id": payload.participant_id,
        "answers": answer_vector,
        "profile": profile,
        "timestamp": datetime.now().isoformat(),
        "ai_feature_vector": build_ai_feature_vector(answer_vector).tolist(),
    }
    
    # 4. Store in memory
    participants[payload.participant_id] = {...}
    profile_snapshots.append(snapshot)
    
    # 5. Compare with existing participants
    similarities = []
    for other_id, other_data in participants.items():
        if other_id == payload.participant_id:
            continue
        score = compute_similarity(answer_vector, other_data["answers"])
        if score >= 0.9:
            similarities.append({...})
    
    # 6. Return response
    return {
        "participant_id": payload.participant_id,
        "profile": profile,
        "highly_similar_participants": similarities,
    }
```

**Time Complexity:**
- Profile generation: O(1) - constant time
- Similarity comparison: O(n × m) where n = existing participants, m = feature vector size (26)
- For 200 participants: ~200 × 26 = 5,200 operations (very fast)

**Error Handling:**
```python
try:
    features_a = build_ai_feature_vector(vec_a)
    # ... computation
except Exception as e:
    # Fall back to exact matching
    return exact_ratio
```

---

### 7. Frontend-Backend Communication

**Question: How does the frontend send and receive data?**

**Request Structure:**
```javascript
const response = await fetch(`${API_BASE}/api/submit`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        participant_id: "user123",
        participant_name: "John Doe",  // Optional
        answers: [
            { question_id: "ack_1", option_value: 2 },
            { question_id: "ack_2", option_value: 3 },
            // ... 12 total
        ],
    }),
});
```

**Response Structure:**
```json
{
    "participant_id": "user123",
    "participant_name": "John Doe",
    "profile": {
        "dimensions": {
            "emotional_clarity": 0.67,
            "stress_management": 0.44,
            ...
        },
        "summary": "You show strong emotional awareness..."
    },
    "highly_similar_participants": [
        {
            "participant_id": "user456",
            "participant_name": "Jane Smith",
            "similarity": 0.92,
            "similarity_percentage": 92.0
        }
    ],
    "has_similar_matches": true,
    "submission_timestamp": "2024-01-15T10:30:00"
}
```

**API Base URL Detection:**
```javascript
const getApiBase = () => {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return port ? `${protocol}//${hostname}:${port}` 
                    : `${protocol}//${hostname}:8000`;
    }
    
    // Deployed: use same origin
    return port ? `${protocol}//${hostname}:${port}` 
                : `${protocol}//${hostname}`;
};
```

---

### 8. Data Structures & Storage

**Question: How is data stored in memory?**

**Storage Structure:**
```python
# Quick lookup dictionary
participants: Dict[str, Dict[str, Any]] = {
    "user123": {
        "id": "user123",
        "name": "John Doe",
        "answers": {"ack_1": 2, "ack_2": 3, ...},
        "profile": {...},
        "timestamp": "2024-01-15T10:30:00",
    },
    "user456": {...},
}

# Historical snapshots (for future analysis)
profile_snapshots: List[Dict[str, Any]] = [
    {
        "participant_id": "user123",
        "participant_name": "John Doe",
        "answers": {...},
        "profile": {...},
        "timestamp": "2024-01-15T10:30:00",
        "ai_feature_vector": [0.12, 0.23, ...],  # 26 dimensions
    },
    ...
]
```

**Why two structures?**
- **`participants`**: Fast O(1) lookup for similarity comparisons
- **`profile_snapshots`**: Complete history with feature vectors for analysis

**Memory Usage (estimated):**
- Per participant: ~2-3 KB
- 200 participants: ~400-600 KB
- Very lightweight for in-memory storage

---

### 9. Edge Cases & Error Handling

**Question: How are edge cases handled?**

**1. Empty or Missing Answers:**
```python
def build_ai_feature_vector(answer_vector: Dict[str, int]) -> np.ndarray:
    base_features = [answer_vector.get(qid, 0) for qid in question_order]
    # Missing questions default to 0
```

**2. NaN Values:**
```python
def safe_std(values):
    std_val = np.std(values)
    return std_val if not np.isnan(std_val) else 0.0

# Check before using
if np.any(np.isnan(features_a)) or np.any(np.isnan(features_b)):
    return exact_ratio  # Fall back
```

**3. Zero Vector (All Answers = 0):**
```python
norm = np.linalg.norm(feature_vector)
if norm <= 1e-10:
    feature_vector = np.zeros_like(feature_vector)  # Return zero vector
```

**4. Identical Answers:**
```python
if exact_ratio >= 1.0:
    return 1.0  # Early return, skip computation
```

**5. Empty Participant List:**
```python
for other_id, other_data in participants.items():
    if other_id == payload.participant_id:
        continue  # Skip self-comparison
    # If participants dict is empty, loop doesn't execute
```

**6. Invalid Cosine Similarity:**
```python
if np.isnan(ai_similarity) or ai_similarity < 0:
    ai_similarity = exact_ratio  # Fall back to exact match
```

---

### 10. Performance Optimization

**Question: How is the system optimized for performance?**

**1. Early Returns:**
```python
if exact_ratio >= 1.0:
    return 1.0  # Skip expensive computation
```

**2. In-Memory Storage:**
- O(1) dictionary lookups
- No database query overhead

**3. Vectorized Operations:**
```python
# NumPy operations are vectorized (C-level speed)
np.mean(values)  # Fast
np.std(values)   # Fast
```

**4. Efficient Similarity Computation:**
```python
# Single matrix operation
similarity_matrix = cosine_similarity(
    features_a.reshape(1, -1),
    features_b.reshape(1, -1)
)
```

**5. Batch Processing:**
- Similarity computed only on submission
- Not continuously recomputed

**Performance Metrics (estimated):**
- Profile generation: < 1ms
- Single similarity comparison: < 1ms
- Full submission (200 participants): < 200ms
- Total API response time: < 300ms

---

### 11. CORS Configuration

**Question: Why is CORS enabled and how does it work?**

**Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
```

**Why needed?**
- Frontend and backend may be on different domains
- Browsers block cross-origin requests by default (Same-Origin Policy)
- CORS allows controlled cross-origin access

**For Production:**
```python
# More secure configuration
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

---

### 12. Deployment Configuration

**Question: How does the deployment configuration work?**

**Render.com (`render.yaml`):**
```yaml
services:
  - type: web
    name: mental-wellbeing-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host=0.0.0.0 --port=$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

**Nixpacks (`nixpacks.toml`):**
```toml
[phases.setup]
nixPkgs = ["python311", "gcc"]

[phases.install]
cmds = [
  "python -m venv /opt/venv",
  ". /opt/venv/bin/activate",
  "pip install --upgrade pip",
  "pip install -r requirements.txt"
]

[start]
cmd = "uvicorn app:app --host=0.0.0.0 --port=$PORT"
```

**Port Configuration:**
```python
port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT not set
# Cloud platforms set PORT environment variable automatically
```

---

## 🔧 Common Technical Questions

### Q: What's the time complexity of similarity detection?

**A:** 
- **Single comparison**: O(m) where m = feature vector size (26) = O(1) constant
- **Full submission with n participants**: O(n × m) = O(n)
- **For 200 participants**: ~200 × 26 = 5,200 operations (< 1ms)

### Q: Why NumPy and scikit-learn?

**A:**
- **NumPy**: Fast vectorized operations, efficient array handling
- **scikit-learn**: Well-tested cosine similarity implementation, optimized C code
- **Alternative**: Could implement cosine similarity manually, but sklearn is faster and more reliable

### Q: Can the algorithm handle missing answers?

**A:** Yes, missing answers default to 0:
```python
base_features = [answer_vector.get(qid, 0) for qid in question_order]
```
However, the frontend validates all questions are answered before submission.

### Q: What happens with negative similarity scores?

**A:** Cosine similarity can theoretically return -1 to 1, but we clamp to 0-1:
```python
final_similarity = max(0.0, min(1.0, combined_similarity))
```
Negative scores are treated as 0 (no similarity).

### Q: How would you scale to 10,000+ participants?

**A:**
1. **Database**: PostgreSQL with indexes on participant_id
2. **Approximate Nearest Neighbor (ANN)**: Use libraries like FAISS or Annoy
3. **Batch Processing**: Compute similarities in background jobs
4. **Caching**: Cache feature vectors in Redis
5. **Sampling**: Only compare with subset of participants initially

---

## 📊 Algorithm Visualization

### Feature Vector Construction Flow:
```
Raw Answers (12 values)
    ↓
Base Features (12 dims)
    ↓
Thematic Aggregation (8 dims)
    ↓
Pattern Analysis (6 dims)
    ↓
Combined Vector (26 dims)
    ↓
L2 Normalization
    ↓
Normalized Feature Vector (26 dims, ||v|| = 1)
```

### Similarity Computation Flow:
```
Participant A Answers → Feature Vector A (26 dims)
Participant B Answers → Feature Vector B (26 dims)
    ↓
Cosine Similarity (A · B)
    ↓
Exact Match Ratio
    ↓
Weighted Combination
    ↓
Final Similarity Score (0-1)
    ↓
Threshold Check (≥ 0.9?)
    ↓
Return Match or No Match
```

---

This technical deep-dive covers the core algorithms and implementation details. Use this for technical interviews, code reviews, or detailed discussions about the system architecture.



