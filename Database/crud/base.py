from services.database import start_database_session


class BaseCRUD():
    def __init__(self, model):
        self.Model = model

    def create(self, db_connection, data):
        new_record = self.Model(**data)
        db_connection.add(new_record)
        db_connection.commit()
        db_connection.refresh(new_record)
        return new_record
    
    def read(self, db_connection, record_id):
        return db_connection.query(self.Model).filter(self.Model.id == record_id).first()
    
    def update(self, db_connection, record_id, data):
        record = db_connection.query(self.Model).filter(self.Model.id == record_id).first()
        if not record:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(record, key, value)
        db_connection.commit()
        db_connection.refresh(record)
        return record

    def delete(self, db_connection, record_id):
        record = db_connection.query(self.Model).filter(self.Model.id == record_id).first()
        if not record:
            return None
        db_connection.delete(record)
        db_connection.commit()
        return record
    def list(self, db_connection):
        return db_connection.query(self.Model).all()
    
    