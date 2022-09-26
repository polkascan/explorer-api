#  Polkascan Harvester
#
#  Copyright 2018-2020 Stichting Polkascan (Polkascan Foundation).
#  This file is part of Polkascan.
#
#  Polkascan is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Polkascan is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Polkascan. If not, see <http://www.gnu.org/licenses/>.
import sqlalchemy as sa

from app.db import BaseModel


class HarvesterStatus(BaseModel):
    __tablename__ = 'harvester_status'

    key = sa.Column(sa.String(64), nullable=False, primary_key=True, index=True)
    description = sa.Column(sa.String(255), nullable=True)
    value = sa.Column(sa.JSON(), nullable=True)

    def __repr__(self):
        return "<{}(key={})>".format(self.__class__.__name__, self.key)
