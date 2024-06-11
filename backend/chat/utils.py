from user.models import UserAccount, FollowedPrograms
from trainer.models import Trainer_profile
from fitness_program.models import FitnessProgram
from asgiref.sync import sync_to_async


# fetch the contacts of a trainer
@sync_to_async
def getTrainerContacts(user):
    trainer = Trainer_profile.objects.get(user=user)
    programs = FitnessProgram.objects.filter(trainer=trainer)
    users = []
    for program in programs:
        user_ids = FollowedPrograms.objects.filter(program=program).values_list('user', flat=True)
        users.extend(UserAccount.objects.filter(pk__in=user_ids))
    users= set(users)
    users = list(users)
    print("The getTrainerContacts users in the chat util : ", users)
    return users
    
@sync_to_async   
def getUserContacts(user):
    programs = FollowedPrograms.objects.filter(user=user)
    trainers = set()
    for followed_program in programs:
        for program in followed_program.program.all():
            # Add the trainer of each followed program to the set of trainers
            trainers.add(program.trainer)
    users = []
    for trainer in trainers:
        # Change here: Get the first instance of UserAccount
        user_instance = UserAccount.objects.filter(trainer_profile=trainer).first()
        if user_instance:
            users.append(user_instance)
    print("The getUserContacts users in chat utils : ", users)
    return users
    



