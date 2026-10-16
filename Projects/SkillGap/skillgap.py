import json

# Used for training and gap-analysis
ROLE_SKILLS = {
    "Python Developer": ["python", "oop", "data structures", "git", "apis", "testing"],
    "Software Engineer": ["python", "oop", "data structures", "algorithms", "git", "databases"],
    "Data Analyst": ["python", "sql", "statistics", "data visualization", "excel", "pandas"],
    "Machine Learning Engineer": ["python", "statistics", "linear algebra", "machine learning", "data structures", "pandas", "numpy"],
    "Web Developer": ["python", "html", "css", "javascript", "apis", "databases"],
}

# Each profile is treated as a data point
TRAINING_DATA = [
    (["python","oop","data structures","git","apis","testing"], "Python Developer"),
    (["python","oop","data structures","algorithms","git","databases"], "Software Engineer"),
    (["python","sql","statistics","data visualization","excel","pandas"], "Data Analyst"),
    (["python","statistics","linear algebra","machine learning","pandas","numpy"], "Machine Learning Engineer"),
    (["python","html","css","javascript","apis","databases"], "Web Developer"),
    (["python","oop","git","apis"], "Python Developer"),
    (["python","data structures","algorithms","git"], "Software Engineer"),
    (["python","sql","statistics","excel"], "Data Analyst"),
    (["python","statistics","machine learning","numpy"], "Machine Learning Engineer"),
    (["html","css","javascript","apis"], "Web Developer"),
    (["python","oop","data structures","algorithms"], "Software Engineer"),
    (["python","sql","pandas","data visualization"], "Data Analyst"),
    (["python","statistics","linear algebra","numpy","pandas"], "Machine Learning Engineer"),
    (["python","oop","apis","testing"], "Python Developer"),
    (["html","css","javascript","databases"], "Web Developer"),
]
def build_vocabulary(training_data):
    vocab = set()
    for profile, _ in training_data:
        vocab.update(profile)
    return sorted(vocab)

def vectorize(skills, vocabulary): # Used to turn a skill to 0 or 1 vector matching
    skill_set = set(skills)
    return [1 if s in skill_set else 0 for s in vocabulary]

def cosine_similarity(vec_a, vec_b): # Used to measure the angle between two vectors
    dot = sum(a*b for a, b in zip(vec_a,vec_b))
    norm_a = sum(a*a for a in vec_a) ** 0.5
    norm_b = sum(b*b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
    

class KNNClassifier:
    def __init__(self, training_data, k=3):
        self.training_data = training_data
        self.k = k
        self.vocabulary = build_vocabulary(training_data)
        self.training_vectors = [
            (vectorize(profile, self.vocabulary),role)
            for profile, role in training_data
        ]

    def predict(self, skills): # Compare user to every training profile
        user_vec = vectorize(skills, self.vocabulary)
        distance = []
        for vec, role in self.training_vectors:
            sim = cosine_similarity(user_vec, vec)
            distance.append((sim, role))
        distance.sort(reverse=True, key= lambda x: x[0])
        top_k = distance[:self.k]
        return self._vote(top_k), top_k

    def _vote(self, neighbors): 
        scores = {}
        for sim, role in neighbors:
            scores[role] = scores.get(role, 0) + sim
        ranked = sorted(scores.items(), key= lambda x: x[1], reverse=True)
        return ranked

class SkillProfile:
    def __init__(self, skills=None):
        self.skills = set(skills or [])

    def add(self, skill):
        self.skills.add(skill.strip().lower())

    def remove(self, skill):
        # Remove one skill
        skill = skill.strip().lower()

        if skill in self.skills:
            self.skills.discard(skill)
            print("Skill removed.")
            return True
        return False

    def erase(self): # Remove all skills
        self.skills.clear()
        

    def save(self, filename="skillgap_data.json"):
        with open(filename, "w") as f:
            json.dump(sorted(self.skills), f, indent=2)

    def load(self, filename="skillgap_data.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("Invalid data format")
                self.skills = set(data)
        except FileNotFoundError:
            print("No saved profile found.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Could not load profile: {e}")

class SkillGapAnalyzer:
    def __init__(self, role_skills):
        self.role_skills = role_skills

    def analyze(self, skills, role):
        required = set(self.role_skills[role])
        current = set(skills)
        matched = current & required
        missing = required - current
        coverage = len(matched) / len(required) * 100
        return matched, missing, coverage

def main():
    profile = SkillProfile()
    profile.load()
    model = KNNClassifier(TRAINING_DATA)
    analyzer = SkillGapAnalyzer(ROLE_SKILLS)

    while True:
        print("""\n=== SkillGap ML ===\n
1. Add skill
2. View skills
3. Remove skill
4. ML role prediction"
5. Analyze a target role
6. Save and exit""")
        choice = input("Choose: ").strip()

        if choice == "1":
            profile.add(input("Skill: "))
            print("Skill added.")

        elif choice == "2":
            print("\nYour skills:")
            for skill in sorted(profile.skills):
                print("-", skill.title())
            if not profile.skills:
                print("No skills added yet.")

        elif choice == "3":
            delete = input("Skill to remove: ").lower()
            if delete == "all":
                profile.erase()
                print("All skills removed.")
            else:
                profile.skills.remove(delete)
                print("Skill removed.")
            
        elif choice == "4":
            if not profile.skills:
                print("Add some skills first.")
                continue
            ranked, predictions = model.predict(profile.skills)
            total = sum(score for _, score in ranked) or 1
            print("\n=== ML Role Prediction ===")
            for role, score in ranked:
                print(f"{role}: {score/total * 100:.3f}%")
            print("\nNearest training examples:")
            for similarity, role in predictions:
                print(f"{role}: similarity= {similarity/total * 100:.3f}%")
            print("\nPrediction uses K-nearest neighbors and cosine similarity.")

        elif choice == "5":
            roles = list(ROLE_SKILLS)
            for i, role in enumerate(roles, 1):
                print(f"{i}. {role}")
            try:
                role = roles[int(input("Choose role: ")) - 1]
            except (ValueError, IndexError):
                print("Invalid choice.")
                continue
            matched, missing, coverage = analyzer.analyze(profile.skills, role)
            print(f"\n{role}")
            print(f"Skill coverage: {coverage:.1f}%")
            print("Matched:", ", ".join(sorted(matched)) or "None")
            print("Missing:", ", ".join(sorted(missing)) or "None")

        elif choice == "6":
            profile.save()
            print("Profile saved. Goodbye!")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
