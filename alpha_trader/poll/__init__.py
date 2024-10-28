from pydantic import BaseModel
from alpha_trader.company import Company
from alpha_trader.user import User
from alpha_trader.vote import Vote


class PollGroup(BaseModel):
    group_member: User
    number_of_voices: int


class Poll(BaseModel):
    abstention_rule: str
    approval_votes_percentage: float
    cast_approval_votes_percentage: float
    cast_refusal_votes_percentage: float
    cast_votes_percentage: float
    company: Company
    end_date: int
    id: str
    left_votes_percentage: float
    motion: str
    poll_initiator: User
    refusal_votes_percentage: float
    result_expire_date: int
    start_date: int
    total_number_of_cast_votes: int
    total_number_of_voices: int
    type: str
    version: int
    votes: list[Vote]
    group: list[PollGroup]

    @staticmethod
    def initialize_from_api_response(api_response: dict):
        return Poll(
            abstention_rule=api_response["abstentionRule"],
            approval_votes_percentage=api_response["approvalVotesPercentage"],
            cast_approval_votes_percentage=api_response["castApprovalVotesPercentage"],
            cast_refusal_votes_percentage=api_response["castRefusalVotesPercentage"],
            cast_votes_percentage=api_response["castVotesPercentage"],
            company=Company.initialize_from_api_response(api_response["company"]),
            end_date=api_response["endDate"],
            id=api_response["id"],
            left_votes_percentage=api_response["leftVotesPercentage"],
            motion=api_response["motion"],
            poll_initiator=User.initialize_from_api_response(api_response["pollInitiator"]),
            refusal_votes_percentage=api_response["refusalVotesPercentage"],
            result_expire_date=api_response["resultExpireDate"],
            start_date=api_response["startDate"],
            total_number_of_cast_votes=api_response["totalNumberOfCastVotes"],
            total_number_of_voices=api_response["totalNumberOfVoices"],
            type=api_response["type"],
            version=api_response["version"],
            votes=[Vote.initialize_from_api_response(vote) for vote in api_response["votes"]],
            group=[PollGroup(group_member=group["groupMember"], number_of_voices=group["numberOfVoices"]) for group in api_response["group"]]
        )
