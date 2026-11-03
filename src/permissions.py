def puede_modificar(user, student_id, group_id, con):
    if not user:
        return False

    u = dict(user) if not isinstance(user, dict) else user
    
    # 1. Verificar rol (convertido a minúsculas)
    role = str(u.get("role", "")).lower()
    if role != "profesor":
        return False

    try:
        s_id = int(student_id)
        g_id = int(group_id)
        u_id = int(u.get("id"))
    except (ValueError, TypeError):
        return False

    # 2. Verificar que el profesor sea dueño del grupo Y que el estudiante esté inscrito (enrollments)
    query = """
        SELECT 1 
        FROM groups g
        JOIN enrollments e ON g.id = e.group_id
        WHERE g.professor_id = ? AND g.id = ? AND e.student_id = ?
    """
    row = con.execute(query, (u_id, g_id, s_id)).fetchone()
    return row is not None


def puede_consultar(user, student_id, group_id, con):
    if not user:
        return False

    u = dict(user) if not isinstance(user, dict) else user
    role = str(u.get("role", "")).lower()

    try:
        s_id = int(student_id)
        g_id = int(group_id)
        u_id = int(u.get("id"))
    except (ValueError, TypeError):
        return False

    if role == "administrador":
        return True

    if role == "profesor":
        return puede_modificar(user, student_id, group_id, con)

    if role == "estudiante":
        # Comprobar que sea el propio estudiante
        u_student_id = u.get("student_id") if u.get("student_id") is not None else u_id
        if int(u_student_id) != s_id:
            return False

        # Verificar que esté inscrito en la tabla enrollments
        query = "SELECT 1 FROM enrollments WHERE student_id = ? AND group_id = ?"
        row = con.execute(query, (s_id, g_id)).fetchone()
        return row is not None

    return False