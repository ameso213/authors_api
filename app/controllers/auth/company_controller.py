from flask import Blueprint, request, jsonify
from app.models.companies import Company, db
from app.models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity

company_bp = Blueprint('company', __name__, url_prefix='/api/v1/company')

# Register a new company
@company_bp.route('/register', methods=['POST'])
@jwt_required()  # Only authenticated users can access this route
def register_company():
    try:
        # Extract request data
        name = request.json.get('name')
        origin = request.json.get('origin')
        description = request.json.get('description')

        # Validate input
        if not name:
            return jsonify({"error": 'Company name is required'}), 400
        

        if not origin:
            return jsonify({"error": 'Company origin is required'}), 400

        if not description:
            return jsonify({"error": 'Company description is required'}), 400
        
        if Company.query.filter_by(name=name).first():
            return jsonify({"error": 'Company name already exists'})

        # Get user ID from JWT token
        user_id = get_jwt_identity()

        # Create new company associated with the user
        new_company = Company(
            name=name,
            origin=origin,
            description=description,
            user_id=user_id
        )

        # Add company to the database
        db.session.add(new_company)
        db.session.commit()

        # Response message
        message = f"Company '{new_company.name}' with ID '{new_company.id}' has been registered"
        return jsonify({"message": message,
                        "company": {
                            'id': new_company.id,
                            'name': new_company.name,
                            'origin': new_company.origin,
                            'description': new_company.description,
                            'user_id': new_company.user_id
                        }}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Get all companies
@company_bp.route('/', methods=['GET'])
@jwt_required()  # Only authenticated users can access this route
def get_all_companies():
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()

        # Get user details
        user = User.query.get(user_id)

        # Check if user is admin
        if user.user_type != 'admin':
            return jsonify({"error": "You are not authorized to access this route"}), 403

        # Retrieve all companies
        companies = Company.query.all()
        company_data = [{
            "id": company.id,
            "name": company.name,
            "origin": company.origin,
            "description": company.description,
            "user_id": company.user_id
        } for company in companies]

        return jsonify({"companies": company_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get company by ID
@company_bp.route('/company/<int:id>', methods=['GET'])
@jwt_required()  # Only authenticated users can access this route
def get_company(id):
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()

        # Get user details
        user = User.query.get(user_id)

        # Retrieve company by ID
        company = Company.query.get(id)

        # Check if user is admin or owner of the company
        if user.user_type != 'admin' and company.user_id != user_id:
            return jsonify({"error": "You are not authorized to access this company"}), 403

        # Return company details
        company_data = {
            "id": company.id,
            "name": company.name,
            "origin": company.origin,
            "description": company.description,
            "user_id": company.user_id
        }

        return jsonify(company_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update company details
@company_bp.route('/company/<int:id>', methods=['PUT'])
@jwt_required()  # Only authenticated users can access this route
def update_company(id):
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()

        # Retrieve company by ID
        company = Company.query.get(id)

        # Check if the company exists
        if not company:
            return jsonify({"error": "Company not found"}), 404

        # Check if user is admin or owner of the company
        if user_id != company.user_id:
            return jsonify({"error": "You are not authorized to update this company"}), 403

        # Update company details
        company.name = request.json.get('name', company.name)
        company.origin = request.json.get('origin', company.origin)
        company.description = request.json.get('description', company.description)

        db.session.commit()

        return jsonify({"message": "Company updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    
# Delete company
@company_bp.route('/company/<int:id>', methods=['DELETE'])

@jwt_required()  # Only authenticated users can access this route
def delete_company(id):
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()

        # Retrieve company by ID
        company = Company.query.get(id)

        # Check if the company exists
        if not company:
            return jsonify({"error": "Company not found"}), 404

        # Check if user is admin or owner of the company
        if user_id != company.user_id:
            return jsonify({"error": "You are not authorized to delete this company"}), 403

        # Delete company
        db.session.delete(company)
        db.session.commit()

        return jsonify({"message": "Company deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),500