from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = '1234' 


def get_db_connection():
    conn = sqlite3.connect('employee_data.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        role = request.form['role'] 
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if role == 'organization':
                cursor.execute('INSERT INTO organizations (name, email, phone_number, password) VALUES (?, ?, ?, ?)', 
                               (name, email, phone_number, password))
            elif role == 'employee':
                cursor.execute('INSERT INTO employees (name, email, phone_number, password) VALUES (?, ?, ?, ?)', 
                               (name, email, phone_number, password))
            conn.commit()
            flash('Signup successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.', 'error')
        finally:
            conn.close()

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if role == 'organization':
            user = conn.execute('SELECT * FROM organizations WHERE email = ? AND password = ?', (email, password)).fetchone()
            if user:
                flash('Login successful!', 'success')
                return redirect(url_for('org_dashboard'))
            else:
                flash('Invalid credentials. Please try again.', 'error')
        elif role == 'employee':
            user = conn.execute('SELECT * FROM employees WHERE email = ? AND password = ?', (email, password)).fetchone()
            if user:
                flash('Login successful!', 'success')
                return redirect(url_for('emp_dashboard'))
            else:
                flash('Invalid credentials. Please try again.', 'error')
        conn.close()

    return render_template('login.html')


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/org_dashboard',methods=['POST','GET'])
def org_dashboard():
    return render_template('org.html')

@app.route('/emp_dashboard',methods=['POST','GET'])
def emp_dashboard():
    data = pd.read_csv('tech_layoffs.csv')

    
    unique_stages = data['Stage'].dropna().unique().tolist()
    unique_industries = data['Industry'].dropna().unique().tolist()
    unique_countries = data['Country'].dropna().unique().tolist()
    unique_continents = data['Continent'].dropna().unique().tolist()
    unique_companies = data['Company'].dropna().unique().tolist()

    return render_template('emp.html', 
                           stages=unique_stages, 
                           industries=unique_industries, 
                           countries=unique_countries, 
                           continents=unique_continents, 
                           companies=unique_companies)
    


@app.route('/predict', methods=['POST'])
def predict():
    prediction_type = request.form['prediction_type']
    
    if prediction_type == 'attrition':
        model = joblib.load('models/models_attrition/attrition_xgboost_model.pkl')
        le_attrition = joblib.load('models/models_attrition/attrition_encoder.pkl')
        scaler = joblib.load('models/models_attrition/attrition_scaler.pkl')
        imputer = joblib.load('models/models_attrition/attrition_imputer.pkl')
        le_department = joblib.load('models/models_attrition/department_encoder.pkl')
        le_gender = joblib.load('models/models_attrition/gender_encoder.pkl')
        le_martial = joblib.load('models/models_attrition/martial_encoder.pkl')
        le_overtime = joblib.load('models/models_attrition/overtime_encoder.pkl')

        age = float(request.form['Age'])
        department = le_department.transform([request.form['department']])[0]
        distance_from_home = float(request.form['distanceFromHome'])
        gender = le_gender.transform([request.form['gender']])[0]
        martial_status = le_martial.transform([request.form['maritalStatus']])[0]
        monthly_income = float(request.form['monthlyIncome'])
        over_time = le_overtime.transform([request.form['overTime']])[0]
        percent_salary_hike = float(request.form['percentSalaryHike'])
        work_life_balance = int(request.form['workLifeBalance'])
        years_at_company = float(request.form['yearsAtCompany'])
        years_with_curr_manager = float(request.form['yearsWithCurrentManager'])

        user_data = [[age, department, distance_from_home, gender, martial_status, monthly_income, 
                      over_time, percent_salary_hike, work_life_balance, years_at_company, years_with_curr_manager]]
        
        user_data_imputed = imputer.transform(user_data)
        user_data_scaled = scaler.transform(user_data_imputed)
        prediction = model.predict(user_data_scaled)
        attrition_result = le_attrition.inverse_transform(prediction)
        li=[department,distance_from_home,gender,martial_status,monthly_income,age,over_time,percent_salary_hike,work_life_balance,years_at_company,years_with_curr_manager]
        return render_template('result.html', prediction=attrition_result,pred=li)

    elif prediction_type == 'layoff':
        layoff_model = joblib.load('models/models_layoff/layoff_model.pkl')
        le_company = joblib.load('models/models_layoff/company_encoder_layoff.pkl')
        le_continent = joblib.load('models/models_layoff/continent_encode_layoff.pkl')
        le_country = joblib.load('models/models_layoff/country_encoder_layoff.pkl')
        le_industry = joblib.load('models/models_layoff/industry_encoder_layoff.pkl')
        rfe_layoff = joblib.load('models/models_layoff/rfe_layoff.pkl')
        scaler_layoff = joblib.load('models/models_layoff/scaler_layoff.pkl')
        le_stage = joblib.load('models/models_layoff/stage_encoder_layoff.pkl')

        input_data = {
            'Company': request.form['company'],
            'Company_Size': request.form['company_size'],
            'Country': request.form['country'],
            'Continent': request.form['continent'],
            'Industry': request.form['industry'],
            'Stage': request.form['stage'],
            'Money_Raised_in_$_mil': float(request.form['funds_raised']),
            'year': int(request.form['year']),
            'month': int(request.form['month']),
            'quarter': int(request.form['quarter']),
            'day_of_week': int(request.form['day']),
        }
        
        df = pd.DataFrame([input_data])

        df['Company']=le_company.transform(df['Company'])
        df['Country']=le_country.transform(df['Country'])
        df['Continent']=le_continent.transform(df['Continent'])
        df['Industry']=le_industry.transform(df['Industry'])
        df['Stage']=le_stage.transform(df['Stage'])

        
        df_scaled = scaler_layoff.transform(df)
        input_rfe = rfe_layoff.transform(df_scaled)
        prediction_result = layoff_model.predict(input_rfe)
        li2=[input_data['Stage'],input_data['Industry'],input_data['Country'],input_data['Continent'],input_data['Company'],input_data['Company_Size'],input_data['Money_Raised_in_$_mil'],input_data['year'],input_data['month'],input_data['quarter'],input_data['day_of_week']]
        
        return render_template('layoff_result.html', ans=prediction_result,predi=li2)

if __name__ == '__main__':
    app.run(debug=True)
