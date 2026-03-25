import enum

class AccountType(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    REMOVED = "removed"

class StorageType(str, enum.Enum):
    ALLOCATED = "ALLOCATED"
    UNALLOCATED = "UNALLOCATED"

class TransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class VaultStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FULL = "FULL"
    MAINTENANCE = "MAINTENANCE"
