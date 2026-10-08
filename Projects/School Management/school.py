import json

FILE = "school.json"

class Person:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def show(self):
        return f"{self.id} | {self.name} | {self.email}"

    def data(self):
        return {"id": self.id, "name": self.name, "email": self.email}

class Student(Person):
    def __init__(self, id, name, email, grade):
        super().__init__(id, name, email)
        self.grade = grade

    def show(self):
        return f"{super().show()} | Grade {self.grade}"

    def data(self):
        d = super().data()
        d["grade"] = self.grade
        d["type"] = "student"
        return d

class Teacher(Person):
    def __init__(self, id, name, email, subject):
        super().__init__(id, name, email)
        self.subject = subject

    def show(self):
        return f"{super().show()} | Subject: {self.subject}"

    def data(self):
        d = super().data()
        d["subject"] = self.subject
        d["type"] = "teacher"
        return d

class Course:
    def __init__(self, code, name, teacher, capacity, credits):
        self.code = code
        self.name = name
        self.teacher = teacher
        self.capacity = capacity
        self.credits = credits
        self.grades = {}   

    def show(self):
        n = len(self.grades)
        return f"{self.code} | {self.name} | Teacher: {self.teacher} | {n}/{self.capacity}"

    def data(self):
        return {
            "code": self.code,
            "name": self.name,
            "teacher": self.teacher,
            "capacity": self.capacity,
            "credits": self.credits,
            "grades": self.grades,
        }

class School:
    def __init__(self, name):
        self.name = name
        self.students = {}
        self.teachers = {}
        self.courses = {}
        self.next_student = 1
        self.next_teacher = 1
        self.next_course = 101 

    def new_student(self, name, email, grade):
        sid = f"S{self.next_student:03d}"
        self.next_student += 1
        self.students[sid] = Student(sid, name, email, grade)
        return sid

    def new_teacher(self, name, email, subject):
        tid = f"T{self.next_teacher:03d}"
        self.next_teacher += 1
        self.teachers[tid] = Teacher(tid, name, email, subject)
        return tid

    def new_course(self, name, teacher, capacity, credits):
        teacher = teacher.strip().upper()
        if teacher not in self.teachers:
            raise ValueError("No such teacher.")
        if capacity <= 0 or credits <= 0:
            raise ValueError("Capacity and credits must be positive.")

        code = f"C{self.next_course}"
        self.next_course += 1
        self.courses[code] = Course(code, name, teacher, capacity, credits)
        return code

    def enroll(self, sid, code):
        sid = sid.strip().upper()
        code = code.strip().upper()

        if sid not in self.students:
            raise ValueError("No such student.")
        if code not in self.courses:
            raise ValueError("No such course.")

        course = self.courses[code]
        if sid in course.grades:
            raise ValueError("Already enrolled.")
        if len(course.grades) >= course.capacity:
            raise ValueError("Course is full.")

        course.grades[sid] = None

    def drop(self, sid, code):
        sid = sid.strip().upper()
        code = code.strip().upper()

        if sid not in self.students:
            raise ValueError("No such student.")
        if code not in self.courses:
            raise ValueError("No such course.")
        if sid not in self.courses[code].grades:
            raise ValueError("Not enrolled in that course.")

        del self.courses[code].grades[sid]

    def set_grade(self, sid, code, grade):
        sid = sid.strip().upper()
        code = code.strip().upper()

        if sid not in self.students:
            raise ValueError("No such student.")
        if code not in self.courses:
            raise ValueError("No such course.")

        course = self.courses[code]
        if sid not in course.grades:
            raise ValueError("Not enrolled in that course.")
        if not 0 <= grade <= 100:
            raise ValueError("Grade must be 0-100.")

        course.grades[sid] = grade

    def report(self, sid):
        sid = sid.strip().upper()
        if sid not in self.students:
            raise ValueError("No such student.")

        student = self.students[sid]
        print(f"\nReport card: {student.name} ({student.id})")

        points = 0
        credits = 0
        any_courses = False

        for course in self.courses.values():
            if sid not in course.grades:
                continue
            any_courses = True
            g = course.grades[sid]
            gtext = "not graded" if g is None else str(g)

            if g is not None:
                points += g * course.credits
                credits += course.credits

            print(f"{course.code} | {course.name} | {gtext} | {course.credits} cr")

        if not any_courses:
            print("No courses.")

        if credits:
            print(f"GPA: {points / credits:.2f}")

    def course_report(self, code):
        code = code.strip().upper()
        if code not in self.courses:
            raise ValueError("No such course.")

        course = self.courses[code]
        print(f"\n{course.name} ({course.code})")
        print(f"Teacher: {course.teacher} | {course.credits} cr")
        print(f"Enrolled: {len(course.grades)}/{course.capacity}")
        print("-" * 50)

        if not course.grades:
            print("Nobody enrolled yet.")
            return

        graded = []

        for sid, g in course.grades.items():
            name = self.students[sid].name if sid in self.students else sid
            gtext = "not graded" if g is None else str(g)
            print(f"{sid} | {name} | {gtext}")
            if g is not None:
                graded.append(g)

        if graded:
            print("-" * 50)
            print(f"Avg: {sum(graded)/len(graded):.2f}  "
                  f"High: {max(graded)}  Low: {min(graded)}")

    def save(self):
        data = {
            "name": self.name,
            "next_student": self.next_student,
            "next_teacher": self.next_teacher,
            "next_course": self.next_course,
            "students": [s.data() for s in self.students.values()],
            "teachers": [t.data() for t in self.teachers.values()],
            "courses": [c.data() for c in self.courses.values()],
        }
        with open(FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        try:
            with open(FILE) as f:
                data = json.load(f)
        except FileNotFoundError:
            return  

        self.name = data.get("name", self.name)
        self.next_student = data.get("next_student", 1)
        self.next_teacher = data.get("next_teacher", 1)
        self.next_course = data.get("next_course", 101)

        for s in data.get("students", []):
            self.students[s["id"]] = Student(
                s["id"], s["name"], s["email"], s["grade"])

        for t in data.get("teachers", []):
            self.teachers[t["id"]] = Teacher(
                t["id"], t["name"], t["email"], t["subject"])

        for c in data.get("courses", []):
            course = Course(
                c["code"], c["name"], c["teacher"],
                c["capacity"], c["credits"])
            course.grades = c.get("grades", {})
            self.courses[course.code] = course

def ask(msg):
    return input(msg).strip()

def show_menu():
    print()
    print("""1. Add Student
2. Add Teacher
3. Add Course
4. Enroll
5. Unenroll
6. Set Grade
7. Students
8. Teachers
9. Courses
10. Report Card 
11. Course Report
12. Save
13. Save and Quit""")


def do_add_student(school):
    name = ask("Name: ")
    email = ask("Email: ")
    grade = int(ask("Grade level: "))
    sid = school.new_student(name, email, grade)
    print(f"Student Added With Code: {sid}.")


def do_add_teacher(school):
    name = ask("Name: ")
    email = ask("Email: ")
    subject = ask("Subject: ")
    tid = school.new_teacher(name, email, subject)
    print(f"Teacher Added With Code: {tid}.")


def do_add_course(school):
    name = ask("Course name: ")
    teacher = ask("Teacher ID: ")
    cap = ask("Capacity [30]: ")
    cred = ask("Credits [3]: ")
    cap = 30 if cap == "" else int(cap)
    cred = 3 if cred == "" else int(cred)
    code = school.new_course(name, teacher, cap, cred)
    print(f"Course Added With Code: {code}.")


def do_enroll(school):
    sid = ask("Student ID: ")
    code = ask("Course code: ")
    school.enroll(sid, code)
    print("Enrolled.")


def do_drop(school):
    sid = ask("Student ID: ")
    code = ask("Course code: ")
    school.drop(sid, code)
    print("Unenrolled.")


def do_set_grade(school):
    sid = ask("Student ID: ")
    code = ask("Course code: ")
    grade = float(ask("Grade: "))
    school.set_grade(sid, code, grade)
    print("Grade saved.")


def do_list_students(school):
    if not school.students:
        print("No students yet.")
        return
    print()
    for s in school.students.values():
        print(s.show())


def do_list_teachers(school):
    if not school.teachers:
        print("No teachers yet.")
        return
    print()
    for t in school.teachers.values():
        print(t.show())


def do_list_courses(school):
    if not school.courses:
        print("No courses yet.")
        return
    print()
    for c in school.courses.values():
        print(c.show())


def main():
    school = School("My School")
    school.load()

    while True:
        show_menu()
        choice = ask("Choice: ")

        try:
            if choice == "1":
                do_add_student(school)
            elif choice == "2":
                do_add_teacher(school)
            elif choice == "3":
                do_add_course(school)
            elif choice == "4":
                do_enroll(school)
            elif choice == "5":
                do_drop(school)
            elif choice == "6":
                do_set_grade(school)
            elif choice == "7":
                do_list_students(school)
            elif choice == "8":
                do_list_teachers(school)
            elif choice == "9":
                do_list_courses(school)
            elif choice == "10":
                school.report(ask("Student ID: "))
            elif choice == "11":
                school.course_report(ask("Course code: "))
            elif choice == "12":
                school.save()
                print("Saved.")
            elif choice == "13":
                school.save()
                print("Bye.")
                break
            else:
                print("Pick 1-13.")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
