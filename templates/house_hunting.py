//calculating how many months I need to save the money fo portion_down_payment

total_cost = int(input("The cost of your dream house: "))
portion_down_payment = total_cost/4
current_savings = 0
annual_salary= int(input("Your annual salary: "))
portion_saved = float(input("Portion of your salary to save as a decimal: "))
monthly_salary = annual_salary/12

percent_of_monthly_salary_to_save = monthly_salary * portion_saved

months=0

while current_savings < portion_down_payment:
    investment_savings = (current_savings * 0.04) / 12
    current_savings= current_savings+ percent_of_monthly_salary_to_save+ investment_savings
    months +=1
    if current_savings >= portion_down_payment:
        print(months)


