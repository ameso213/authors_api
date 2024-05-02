from flask import Blueprint
from app.controllers.auth import revokedTokenController

revoked_tokens_bp = Blueprint('revoked_tokens', __name__)

# Define routes for managing revoked tokens
@revoked_tokens_bp.route('/add', methods=['POST'])
def add_revoked_token():
    # Your code here to parse request data and call RevokedTokenController.add_revoked_token
    pass

@revoked_tokens_bp.route('/check', methods=['POST'])
def check_revoked_token():
    # Your code here to parse request data and call RevokedTokenController.check_revoked_token
    pass

@revoked_tokens_bp.route('/remove', methods=['DELETE'])
def remove_revoked_token():
    # Your code here to parse request data and call RevokedTokenController.remove_revoked_token
    pass