
# Practical 6: Mechanical Engineering Calculation and Analysis System

history = []


def get_positive_number(prompt, allow_zero=False):
    """Read and validate a numeric input."""
    while True:
        try:
            value = float(input(prompt))

            if value < 0 or (value == 0 and not allow_zero):
                if allow_zero:
                    print("Error: Value cannot be negative.")
                else:
                    print("Error: Enter a value greater than zero.")
                continue

            return value

        except ValueError:
            print("Invalid input! Please enter a numeric value.")


def show_result(name, formula, values, result, unit):
    """Display and store calculation details."""
    result = round(result, 3)

    print("\n------ Calculation Result ------")
    print("Calculation:", name)
    print("Formula:", formula)

    for parameter, value in values.items():
        print(f"{parameter}: {value:g}")

    print(f"Result: {result:g} {unit}")
    print("--------------------------------")

    history.append({
        "calculation": name,
        "formula": formula,
        "result": result,
        "unit": unit
    })


def calculate_force():
    print("\nFORCE CALCULATION")
    print("Formula: F = m * a")
    print("m = mass (kg), a = acceleration (m/s^2)")

    mass = get_positive_number("Enter mass (kg): ")
    acceleration = get_positive_number(
        "Enter acceleration (m/s^2): ", allow_zero=True
    )

    show_result(
        "Force", "F = m * a",
        {"Mass (kg)": mass, "Acceleration (m/s^2)": acceleration},
        mass * acceleration, "N"
    )


def calculate_work():
    print("\nWORK CALCULATION")
    print("Formula: W = F * d")
    print("F = force (N), d = displacement (m)")
    print("Assumption: Force acts along the displacement.")

    force = get_positive_number("Enter force (N): ", allow_zero=True)
    distance = get_positive_number(
        "Enter displacement (m): ", allow_zero=True
    )

    show_result(
        "Work", "W = F * d",
        {"Force (N)": force, "Displacement (m)": distance},
        force * distance, "J"
    )


def calculate_power():
    print("\nPOWER CALCULATION")
    print("Formula: P = W / t")
    print("W = work (J), t = time (seconds)")

    work = get_positive_number("Enter work (J): ", allow_zero=True)
    time = get_positive_number("Enter time (seconds): ")

    show_result(
        "Power", "P = W / t",
        {"Work (J)": work, "Time (s)": time},
        work / time, "W"
    )


def calculate_pressure():
    print("\nPRESSURE CALCULATION")
    print("Formula: p = F / A")
    print("F = force (N), A = area (m^2)")

    force = get_positive_number("Enter force (N): ", allow_zero=True)
    area = get_positive_number("Enter area (m^2): ")

    show_result(
        "Pressure", "p = F / A",
        {"Force (N)": force, "Area (m^2)": area},
        force / area, "Pa"
    )


def calculate_density():
    print("\nDENSITY CALCULATION")
    print("Formula: density = mass / volume")
    print("Mass in kg, volume in m^3")

    mass = get_positive_number("Enter mass (kg): ", allow_zero=True)
    volume = get_positive_number("Enter volume (m^3): ")

    show_result(
        "Density", "rho = m / V",
        {"Mass (kg)": mass, "Volume (m^3)": volume},
        mass / volume, "kg/m^3"
    )


def calculate_speed():
    print("\nSPEED CALCULATION")
    print("Formula: v = d / t")
    print("d = distance (m), t = time (seconds)")

    distance = get_positive_number(
        "Enter distance (m): ", allow_zero=True
    )
    time = get_positive_number("Enter time (seconds): ")

    show_result(
        "Speed", "v = d / t",
        {"Distance (m)": distance, "Time (s)": time},
        distance / time, "m/s"
    )


def calculate_torque():
    print("\nTORQUE CALCULATION")
    print("Formula: Torque = F * r")
    print("F = force (N), r = perpendicular lever arm (m)")

    force = get_positive_number("Enter force (N): ", allow_zero=True)
    radius = get_positive_number(
        "Enter lever arm (m): ", allow_zero=True
    )

    show_result(
        "Torque", "Torque = F * r",
        {"Force (N)": force, "Lever arm (m)": radius},
        force * radius, "N.m"
    )


def calculate_gear_ratio():
    print("\nGEAR RATIO CALCULATION")
    print("Formula: GR = Teeth on driven gear / Teeth on driver gear")

    driver = get_positive_number(
        "Enter teeth on driver gear: "
    )
    driven = get_positive_number(
        "Enter teeth on driven gear: "
    )

    ratio = driven / driver

    show_result(
        "Gear Ratio", "GR = N2 / N1",
        {"Driver gear teeth (N1)": driver,
         "Driven gear teeth (N2)": driven},
        ratio, ":1"
    )


def show_history():
    print("\n========== CALCULATION HISTORY ==========")

    if not history:
        print("No calculations have been performed yet.")
        return

    for index, item in enumerate(history, start=1):
        print(f"\n{index}. {item['calculation']}")
        print("Formula:", item["formula"])
        print(f"Result: {item['result']:g} {item['unit']}")

    print("\nTotal calculations:", len(history))
    print("=========================================")


def main():
    calculations = {
        "1": calculate_force,
        "2": calculate_work,
        "3": calculate_power,
        "4": calculate_pressure,
        "5": calculate_density,
        "6": calculate_speed,
        "7": calculate_torque,
        "8": calculate_gear_ratio
    }

    while True:
        print("\n========================================")
        print(" MECHANICAL ENGINEERING CALCULATOR")
        print("========================================")
        print("1. Force")
        print("2. Work")
        print("3. Power")
        print("4. Pressure")
        print("5. Density")
        print("6. Speed")
        print("7. Torque")
        print("8. Gear Ratio")
        print("9. View Calculation History")
        print("0. Exit")
        print("========================================")

        choice = input("Select an option (0-9): ").strip()

        if choice in calculations:
            try:
                calculations[choice]()
            except (ArithmeticError, OverflowError) as error:
                print("Calculation error:", error)

        elif choice == "9":
            show_history()

        elif choice == "0":
            print("Thank you for using the Mechanical Calculator!")
            break

        else:
            print("Invalid choice! Please select an option from 0 to 9.")


if __name__ == "__main__":
    main()
