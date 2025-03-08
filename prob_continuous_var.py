lower_limit = -1
upper_limit = 11

sub_lower_lim = -1
sub_upper_lim = 5

probabilty_total = 1/(upper_limit - lower_limit)
probabilty_range = probabilty_total * (sub_upper_lim - sub_lower_lim)
PDF = probabilty_total * (sub_upper_lim - lower_limit)
print("P(X):", round(probabilty_range, 4), "| F(X):", round(PDF, 4))
