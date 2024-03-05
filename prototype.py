from random import randint

def find_max(amounts: [int]) -> (int, int): 
    index = 0 
    max_amount = amounts[0]
    for i, v in enumerate(amounts):
        if max_amount < v:
            index = i
            max_amount = v

    return (index, max_amount)

def pretty_print_dict(v, is_recv, group_size: int):
    if is_recv:
        print("Receivers:")
    else:
        print("Payers:")
    for i in range(group_size):
        print(f"    R{i}: ${v[i]}")

# we assume 2 separate groups. receivers are net owed and payers owe. 
receivers = {}
payers = {}

# all receivers combined need to receive `recv_left` amount, which equals the amount all payers combined need to pay (i.e. pay_left)
recv_left = 5000
pay_left = 5000

# group_size equals no. of receivers and payers. For now we assume both groups are of equal size but it is not necessary to do so. Hence, that total group size (i.e. receivers + payers) is group_size * 2
group_size = 5

# This is just a trick to distribute recv_left and pay_left among receivers and payers. Distribution is biased towards receivers/payers with lower indices and assigns them larger share of the total amount, but that's fine for now.
for i in range(group_size-1):
    v = randint(0, recv_left)
    receivers[i] = v
    recv_left -= v 

    v = randint(0, pay_left)
    payers[i] = v
    pay_left -= v 

    if group_size == i + 2:
        # handle last person
        receivers[i+1] = recv_left
        payers[i+1] = pay_left

print("\nBEFORE SETTLEMENT")
pretty_print_dict(receivers, True, group_size=group_size)
pretty_print_dict(payers, False, group_size=group_size)
print("\n")


last_recv_id = -1
last_pay_id = -1
round_index = 1
while True:

    recv_amounts = []
    pay_amounts = []
    for index in range(group_size):
        recv_amounts.append(receivers[index])
        pay_amounts.append(payers[index])
    
    # we find which of the receivers is owed the most as max_recv_id and which of payers owes the most as max_pay_id. max_pay_id pays max_recv_id minimum of their amounts
    (max_recv_id, _) = find_max(recv_amounts)
    (max_pay_id, _) = find_max(pay_amounts)

    if last_recv_id == max_recv_id and last_pay_id == max_pay_id:
        break

    # how much should max_pay_id pay max_recv_id ?
    #  
    # to_pay equals minimum of amount max_recv_id is owed and max_pay_id owes. There are two ways to find to_pay
    # (1) First is max_pay_id and max_recv_id communicate over a private channel, find to_pay, and max_pay_id sends to_pay amount to max_recv_id
    # (2) Instead of just outputting max_pay_id and max_recv_id, the circuit also outputs to_pay (i.e. min()). This will require an additional min operation. 
    # But I am not sure whether (2) is any better than (1). 
    # Let's say max_pay_id owes 100 and max_recv_id is owed 200, then (2) will output 100. 
    # Hence max_recv_id learns that max_pay_id overall owes 100 AND max_pay_id learns that max_recv_id is owed >= 100. 
    # In this case, max_recv_id has advantage (since it learns max_pay_id's amount) but the same applies if max_recv_id was owed less than max_pay_id owes. 
    to_pay = min(receivers[max_recv_id], payers[max_pay_id])    
    # max_recv_id is now owed to_pay less
    receivers[max_recv_id] -= to_pay
    # max_recv_id nows owes to_pay less
    payers[max_pay_id] -= to_pay

    # we assume a private channel betwee max_recv_id and max_pay_id. 
    print(f'(Round {round_index}) Private channel: P{max_pay_id} pays ${to_pay} to R{max_recv_id}') 
    
    last_recv_id = max_recv_id
    last_pay_id = max_pay_id

    round_index += 1

print("\nAFTER SETTLEMENT")
pretty_print_dict(receivers, True, group_size=group_size)
pretty_print_dict(payers, False, group_size=group_size)